import os
import time
import numpy as np
import pickle
import streamlit as st
from PIL import Image, ImageDraw
from torchvision import transforms

from obj_detection import ObjDetection
from src.utilities import ExactIndex, extract_img, similar_img_search, visualize_outfits
from src.fashion_features import (
    OCCASION_OPTIONS,
    get_dominant_colors,
    rgb_to_hex,
    ai_outfit_rating,
    map_class_to_occasions,
    get_shopping_recommendations,
    authenticate_user,
    save_user_profile,
    load_user_profile,
    save_wardrobe_item,
    get_user_wardrobe,
)


# --- UI Configurations --- #
st.set_page_config(
    page_title="Smart Stylist powered by computer vision",
    page_icon=":shopping_bags:",
    layout='wide'
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.last_image = None
    st.session_state.last_labels = []
    st.session_state.last_occasion = 'Any'
    st.session_state.last_colors = []


def account_sidebar():
    st.sidebar.markdown("# :sparkles: Account")
    if not st.session_state.logged_in:
        choice = st.sidebar.radio("Choose action", ["Login", "Sign Up"])
        username = st.sidebar.text_input("Username", key='user_name')
        password = st.sidebar.text_input("Password", type="password", key='user_pass')
        if st.sidebar.button("Submit"):
            if choice == "Login":
                if authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.sidebar.success(f"Welcome back, {username}!")
                else:
                    st.sidebar.error("Login failed. Check your credentials.")
            else:
                save_user_profile(username, password, wardrobe=[])
                st.session_state.logged_in = True
                st.session_state.username = username
                st.sidebar.success(f"Account created for {username}!")
    else:
        st.sidebar.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Sign Out"):
            st.session_state.logged_in = False
            st.session_state.username = ''
        st.sidebar.markdown("---")
        wardrobe = get_user_wardrobe(st.session_state.username)
        st.sidebar.markdown("### Saved Wardrobe")
        if wardrobe:
            for item in wardrobe[-5:][::-1]:
                st.sidebar.markdown(f"**{item['occasion']}** - {', '.join(item['labels'])}")
        else:
            st.sidebar.info("Your saved wardrobe will appear here.")


def draw_color_palette(colors):
    swatches = []
    for color in colors:
        swatches.append(
            f"<div style='display:inline-block;width:56px;height:56px;margin:2px;border:1px solid #ccc;background:{rgb_to_hex(color)}'></div>"
        )
    st.markdown(''.join(swatches), unsafe_allow_html=True)
    st.write('Palette: ' + ', '.join([rgb_to_hex(c) for c in colors]))


def virtual_tryon_preview(image_obj):
    if image_obj is None:
        return None
    canvas = Image.new('RGB', (420, 520), (245, 245, 245))
    resized = image_obj.convert('RGB').resize((360, 360))
    canvas.paste(resized, (30, 30))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((25, 25, 395, 395), outline=(180, 90, 180), width=4)
    draw.text((30, 420), "Virtual Try-On Preview", fill=(40, 40, 40))
    return canvas


def load_models():
    with st.spinner('Loading models and data...'):
        yolo = ObjDetection(onnx_model='./models/best.onnx', data_yaml='./models/data.yaml')
        with open('img_paths.pkl', 'rb') as im_file:
            image_paths = pickle.load(im_file)
        with open('embeddings.pkl', 'rb') as file:
            embeddings = pickle.load(file)
        loaded_idx = ExactIndex.load(embeddings, image_paths, 'flatIndex.index')
    return yolo, loaded_idx


yolo, loaded_idx = load_models()

transformations = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])


def describe_trend(labels):
    if not labels:
        return "Upload an outfit or use webcam to discover trending fashion details."
    popular = labels[:3]
    return (
        f"Right now, {popular[0].lower()} and {popular[1].lower()} are strong styling choices. "
        f"Mixing {popular[-1].lower()} with complementary textures creates a modern, wearable look."
    )


def fashion_chatbot(question):
    q = question.lower()
    if 'occasion' in q or 'wear' in q:
        return "For an occasion, choose a clean silhouette and an accent accessory. Dresses and jumpsuits are great for parties; shirts and coats work well for the office."
    if 'color' in q:
        return "Neutral base tones are easy to mix. Add one bold color or metallic accessory to make your outfit pop."
    if 'recommend' in q or 'similar' in q:
        return "Your recommendations emphasize shape, color harmony, and texture similarity to the uploaded outfit. Use accessories to complete the look."
    if 'trend' in q:
        return "Current fashion trends favor bold outerwear, monochrome palettes, and statement jewelry."
    return "Ask me about outfit choices, colors, trends, or how to shop similar fashion items."


def analyze_image(image_obj, occasion):
    if image_obj is None:
        return None
    image_array = np.array(image_obj.convert('RGB'))
    cropped_objs = yolo.crop_objects(image_array)
    if not cropped_objs:
        return None

    detected_items = []
    for crop_obj in cropped_objs:
        if isinstance(crop_obj, tuple):
            cropped, label = crop_obj
        else:
            cropped, label = crop_obj, 'Unknown'
        if cropped is None or cropped.size == 0:
            continue
        detected_items.append({'image': cropped, 'label': label})

    labels = [item['label'] for item in detected_items]
    dominant_colors = get_dominant_colors(image_obj)
    rating, commentary = ai_outfit_rating(labels, dominant_colors, occasion)
    shopping = get_shopping_recommendations(labels, dominant_colors)
    occasion_matches = [label for label in labels if occasion != 'Any' and occasion in map_class_to_occasions(label)]

    nearest_paths = []
    for item in detected_items:
        try:
            embedding = extract_img(item['image'], transformations)
            result = similar_img_search(embedding, loaded_idx)
            nearest_paths.extend(result)
        except Exception:
            continue

    return {
        'labels': labels,
        'dominant_colors': dominant_colors,
        'rating': rating,
        'commentary': commentary,
        'shopping': shopping,
        'occasion_matches': occasion_matches,
        'nearest_paths': nearest_paths,
    }


def save_current_outfit(image_obj, labels, occasion, colors):
    if not st.session_state.logged_in:
        st.warning('Sign in to save outfits to your wardrobe.')
        return
    save_wardrobe_item(st.session_state.username, image_obj, labels, occasion, colors)
    st.success('Outfit saved to your wardrobe!')


def main():
    st.markdown("# :female_fairy: :shopping_bags: Smart Stylist")
    st.markdown("## :rainbow: AI Fashion Recommendation Hub")
    st.write("Upload a photo or use live webcam detection to unlock outfit ratings, occasion-aware recommendations, wardrobe saving, and product links.")
    st.divider()

    account_sidebar()

    tabs = st.tabs(["Style Studio", "Virtual Try-On", "Trend Chat", "Gallery"])

    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader('Upload outfit image', type=['png', 'jpg', 'jpeg'])
            camera_file = st.camera_input('Try live webcam detection')
            image_obj = None
            if uploaded_file is not None:
                image_obj = Image.open(uploaded_file)
            elif camera_file is not None:
                image_obj = Image.open(camera_file)

            selected_occasion = st.selectbox('Select occasion', OCCASION_OPTIONS)
            analyze_button = st.button('Analyze Outfit')
            if analyze_button:
                if image_obj is None:
                    st.error('Please upload an image or use the webcam first.')
                else:
                    st.session_state.last_image = image_obj.copy()
                    result = analyze_image(image_obj, selected_occasion)
                    if result is None:
                        st.warning('No fashion objects detected. Try a clearer photo or a different pose.')
                    else:
                        st.session_state.last_labels = result['labels']
                        st.session_state.last_occasion = selected_occasion
                        st.session_state.last_colors = result['dominant_colors']

                        st.markdown('### Outfit Summary')
                        st.metric('AI Outfit Rating', f"{result['rating']} / 5")
                        st.write(result['commentary'])
                        st.markdown('**Detected items:** ' + (', '.join(result['labels']) or 'No items'))
                        if result['occasion_matches']:
                            st.success(f"Matches your selected occasion: {', '.join(result['occasion_matches'])}")
                        else:
                            st.info('We still found strong visual recommendations, even if no single piece maps exactly to the chosen occasion.')

                        st.markdown('### Color Palette')
                        draw_color_palette(result['dominant_colors'])

                        st.markdown('### Shopping Suggestions')
                        for item in result['shopping']:
                            st.markdown(f"- **{item['label']}**: [Shop similar items]({item['link']})")

                        st.markdown('### Similar Looks')
                        if result['nearest_paths']:
                            fig = visualize_outfits(result['nearest_paths'])
                            st.pyplot(fig)
                        else:
                            st.write('No visual recommendations available for this outfit.')

                        if st.button('Save this outfit to wardrobe'):
                            save_current_outfit(image_obj, result['labels'], selected_occasion, result['dominant_colors'])

        with col2:
            st.markdown('### Feature Highlights')
            st.write('- AI Outfit Rating System')
            st.write('- Occasion-Based Recommendations')
            st.write('- Color Palette Detection')
            st.write('- Recommendation Explanation System')
            st.write('- Real-Time Webcam Detection')
            st.write('- Image-to-Product Shopping Links')
            st.write('- User Login + Saved Wardrobe')

    with tabs[1]:
        st.markdown('## Virtual Try-On')
        if st.session_state.last_image is None:
            st.warning('Analyze an outfit in Style Studio first to use virtual try-on.')
        else:
            preview = virtual_tryon_preview(st.session_state.last_image)
            st.image(preview, caption='Virtual Try-On Simulation')
            st.write('This quick preview gives a styling-inspired mockup of your outfit in a fitted display. Use it to explore how the look feels off-camera.')

    with tabs[2]:
        st.markdown('## Fashion Chatbot Assistant')
        question = st.text_input('Ask a fashion question', value='What should I wear for a work presentation?')
        if st.button('Ask Assistant'):
            if question:
                st.write(fashion_chatbot(question))
        st.divider()
        st.markdown('## Fashion Trend Analyzer')
        st.write(describe_trend(st.session_state.last_labels))
        st.write('**Trending categories:** Dresses, Coats, Jewelry, Shoes.')

    with tabs[3]:
        st.markdown('## Gallery')
        st.write('Sample style outcomes and saved wardrobe previews.')
        gallery_col1, gallery_col2 = st.columns(2)
        with gallery_col1:
            st.image('gallery/sample_results/pink-white/pw_im1.png', caption='Sample outfit 1')
            st.image('gallery/sample_results/black-coat/bc_im1.png', caption='Sample outfit 2')
        with gallery_col2:
            st.image('gallery/sample_results/sweater/ss_im1.png', caption='Sample outfit 3')
            st.image('gallery/sample_results/black-jacket/bk_im1.png', caption='Sample outfit 4')

        if st.session_state.logged_in:
            st.markdown('### Your Saved Wardrobe')
            wardrobe = get_user_wardrobe(st.session_state.username)
            if wardrobe:
                for item in wardrobe[::-1]:
                    cols = st.columns([1, 2])
                    with cols[0]:
                        st.image(item['image_path'], width=140)
                    with cols[1]:
                        st.markdown(f"**Occasion:** {item['occasion']}")
                        st.markdown(f"**Items:** {', '.join(item['labels'])}")
                        st.markdown(f"**Palette:** {', '.join(item['colors'])}")
            else:
                st.info('Your wardrobe is empty. Save an analyzed outfit from the Style Studio tab.')
        else:
            st.info('Login to save outfits and view your wardrobe.')


if __name__ == '__main__':
    main()
