import os

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from src.bootstrap import load_yolo, load_embedder_and_db, load_caption_model
from src.personalization import init_session, record_like, record_dislike
from src.ai_features import (
    unpack_detections,
    multimodal_embedding,
    search_similar,
    detect_attributes,
    caption_image,
    rate_outfit,
    predict_trends,
    virtual_try_on,
    transcribe_audio,
    chatbot_reply,
    advanced_ensemble_search,
)
from src.utilities import extract_img_clip, visualize_outfits


st.set_page_config(
    page_title="AI Fashion Intellegence Platform",
    layout="wide",
)

init_session()

st.markdown("#  Smart Stylist")
st.markdown("### Your AI-powered fashion platform")
st.caption(
    "Upload outfits, search by voice or text, get personalized picks, virtual try-on, "
    "trend forecasts, and more — powered by FashionCLIP, YOLO, and ChromaDB."
)

with st.spinner("Loading AI models…"):
    yolo = load_yolo()
    embedder, collection = load_embedder_and_db()

CATEGORIES = ["All", "Shirts_&_Tops", "Dresses", "Pants", "Shoes", "Unknown"]


def category_where(selected: str):
    return None if selected == "All" else {"category": selected}


def show_recommendations(paths, title="Recommendations"):
    if not paths:
        st.warning("No matching items found. Try another query or category.")
        return
    st.markdown(f"**{title}**")
    cols = st.columns(min(len(paths), 3))
    for i, path in enumerate(paths[:6]):
        with cols[i % 3]:
            if path and os.path.exists(path):
                st.image(path, use_container_width=True)
                c1, c2 = st.columns(2)
                if c1.button("👍", key=f"like_{title}_{i}_{path}"):
                    emb = embedder.embed_image(np.array(Image.open(path).convert("RGB")))
                    record_like(path, emb)
                    st.toast("Saved to your style profile")
                if c2.button("👎", key=f"dislike_{title}_{i}_{path}"):
                    record_dislike(path)
                    st.toast("We'll show fewer like this")
    if len(paths) > 3:
        fig = visualize_outfits(paths)
        st.pyplot(fig)
        plt.close(fig)


def upload_image_widget(key: str):
    f = st.file_uploader("Upload image (PNG/JPG)", type=["png", "jpg", "jpeg"], key=key)
    if f is None:
        return None
    return np.array(Image.open(f).convert("RGB"))


feature = st.sidebar.selectbox(
    "Choose a feature",
    [
        "Home & Search",
        "Advanced AI",
        "Virtual Try-On",
        "Fashion Chatbot",
        "Trend Prediction",
        " Smart Attributes",
        " Personalized Engine",
        " Voice Search",
        " Image Captioning",
        " Multi-Modal Search",
        " Fashion Rating",
    ],
)

cat_filter = st.sidebar.selectbox("Category filter", CATEGORIES)
where_clause = category_where(cat_filter)

# --- 1. Home & Search ---
if feature == "Home & Search":
    st.subheader("Visual similarity search")
    st.info("Check the **Gallery** page in the sidebar for sample outfits.")
    text_query = st.text_input("Describe an item (e.g. red dress):")
    img = upload_image_widget("home_upload")

    if text_query and st.button("Search by text"):
        with st.spinner("Searching…"):
            emb = embedder.embed_text(text_query)
            paths = search_similar(embedder, collection, emb, where=where_clause)
            show_recommendations(paths, "Text search results")

    if img is not None:
        st.image(img, caption="Your upload", use_container_width=True)
        if st.button("Search by image"):
            with st.spinner("Detecting fashion items…"):
                crops, labels = unpack_detections(yolo.crop_objects(img))
                if not crops:
                    st.warning("No fashion objects detected.")
                else:
                    boards = []
                    for crop, label in zip(crops, labels):
                        if crop.size > 0:
                            emb = extract_img_clip(crop, embedder)
                            boards.extend(
                                search_similar(embedder, collection, emb, where=where_clause)
                            )
                    show_recommendations(boards, "Image search results")

# --- 2. Advanced AI ---
elif feature == "Advanced AI":
    st.subheader("Advanced AI ensemble")
    st.write(
        "Combines **YOLO detection**, **FashionCLIP embeddings**, and **personalized re-ranking** "
        "for the strongest match quality."
    )
    col1, col2 = st.columns(2)
    with col1:
        adv_text = st.text_input("Optional style description:")
    with col2:
        st.metric("Items in index", collection.count())
    adv_img = upload_image_widget("adv_upload")
    if adv_img is not None and st.button("Run ensemble search"):
        with st.spinner("Running multi-model pipeline…"):
            paths, attrs = advanced_ensemble_search(
                embedder, collection, yolo, adv_img, adv_text or None, where=where_clause
            )
            if attrs:
                st.markdown("**Detected attributes**")
                for a in attrs:
                    st.json(a)
            show_recommendations(paths, "Ensemble results")

# --- 3. Virtual Try-On ---
elif feature == "Virtual Try-On":
    st.subheader("Virtual try-on (preview)")
    st.caption("Overlays a garment onto your photo — best with clear, front-facing shots.")
    person = upload_image_widget("tryon_person")
    garment = upload_image_widget("tryon_garment")
    region = st.radio("Placement", ["torso", "lower", "full"], horizontal=True)
    if person is not None and garment is not None:
        if st.button("Generate try-on preview"):
            result = virtual_try_on(person, garment, region=region)
            st.image(result, caption="Try-on preview", use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                st.image(person, caption="Original", use_container_width=True)
            with c2:
                st.image(garment, caption="Garment", use_container_width=True)

# --- 4. Fashion Chatbot ---
elif feature == "Fashion Chatbot":
    st.subheader("AI fashion assistant")
    for msg in st.session_state.chat_history[-10:]:
        role = msg["role"]
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(msg["content"])

    user_msg = st.chat_input("Ask about styles, trends, or items…")
    if user_msg:
        with st.spinner("Thinking…"):
            reply, paths = chatbot_reply(
                user_msg, embedder, collection, yolo, st.session_state.chat_history
            )
        with st.chat_message("assistant"):
            st.markdown(reply)
        show_recommendations(paths, "Suggested for you")

# --- 5. Trend Prediction ---
elif feature == "Trend Prediction":
    st.subheader("Fashion trend prediction")
    if st.button("Analyze catalog trends"):
        with st.spinner("Analyzing indexed catalog…"):
            trends = predict_trends(collection)
        st.success(f"Current season: **{trends['current_season']}**")
        if trends["categories"]:
            st.bar_chart(trends["categories"])
        if trends["season_hints"]:
            st.markdown("**Seasonal signal strength**")
            st.bar_chart(trends["season_hints"])
        st.write("**Rising categories:**", ", ".join(trends["rising"]) or "—")

# --- 6. Smart Attributes ---
elif feature == "🏷️ Smart Attributes":
    st.subheader("Smart attribute detection")
    st.write("Detects category, color, pattern, and style using YOLO + FashionCLIP.")
    attr_img = upload_image_widget("attr_upload")
    if attr_img is not None and st.button("Detect attributes"):
        with st.spinner("Analyzing…"):
            crops, labels = unpack_detections(yolo.crop_objects(attr_img))
            if not crops:
                attrs = detect_attributes(embedder, attr_img)
                st.json(attrs)
            else:
                for i, (crop, label) in enumerate(zip(crops, labels)):
                    if crop.size > 0:
                        st.image(crop, caption=f"Object {i + 1}: {label}", use_container_width=True)
                        st.json(detect_attributes(embedder, crop, label))

# --- 7. Personalized Engine ---
elif feature == "Personalized Engine":
    st.subheader("Personalized recommendation engine")
    likes = len(st.session_state.liked_paths)
    st.write(f"**Style profile:** {'Active' if st.session_state.style_embedding else 'Not yet — like items below'}")
    st.metric("Liked items", likes)
    query = st.text_input("What are you looking for?")
    use_personal = st.checkbox("Apply my style profile", value=True)
    if query and st.button("Get personalized picks"):
        emb = embedder.embed_text(query)
        paths = search_similar(
            embedder, collection, emb, where=where_clause, personalized=use_personal
        )
        show_recommendations(paths, "For you")
    if st.session_state.liked_paths:
        st.markdown("**Recently liked**")
        for p in st.session_state.liked_paths[-5:]:
            if os.path.exists(p):
                st.image(p, width=120)

# --- 8. Voice Search ---
elif feature == " Voice Search":
    st.subheader("Voice search")
    st.caption("Record a short phrase describing what you want to find.")
    audio = st.audio_input("Record your fashion query")
    voice_text = st.text_input("Or type / edit transcript:")
    if audio is not None:
        transcript = transcribe_audio(audio.getvalue())
        if transcript:
            st.success(f"Heard: **{transcript}**")
            voice_text = transcript
        else:
            st.warning(
                "Could not transcribe audio. Install `SpeechRecognition` or type your query below."
            )
    if voice_text and st.button("Search from voice"):
        emb = embedder.embed_text(voice_text)
        paths = search_similar(embedder, collection, emb, where=where_clause)
        show_recommendations(paths, "Voice search results")

# --- 9. Image Captioning ---
elif feature == "Image Captioning":
    st.subheader("AI image captioning")
    cap_img = upload_image_widget("cap_upload")
    if cap_img is not None and st.button("Generate caption"):
        with st.spinner("Generating caption (BLIP)…"):
            processor, model = load_caption_model()
            caption = caption_image(processor, model, cap_img)
        st.success(caption)
        if st.button("Search catalog from caption"):
            emb = embedder.embed_text(caption)
            paths = search_similar(embedder, collection, emb, where=where_clause)
            show_recommendations(paths, "Matches for caption")

# --- 10. Multi-Modal Search ---
elif feature == " Multi-Modal Search":
    st.subheader("Multi-modal search")
    st.write("Combine **text** and **image** in one query for richer results.")
    mm_text = st.text_input("Text (e.g. floral summer dress):")
    mm_img = upload_image_widget("mm_upload")
    weight = st.slider("Text vs image weight", 0.0, 1.0, 0.5, 0.1)
    if st.button("Multi-modal search"):
        emb = multimodal_embedding(embedder, mm_text, mm_img, text_weight=weight)
        if emb is None:
            st.error("Provide text and/or an image.")
        else:
            paths = search_similar(embedder, collection, emb, where=where_clause)
            show_recommendations(paths, "Multi-modal results")

# --- 11. Fashion Rating ---
elif feature == " Fashion Rating":
    st.subheader("Fashion rating AI")
    st.write("Scores outfit coordination and style using CLIP aesthetic prompts.")
    rate_img = upload_image_widget("rate_upload")
    if rate_img is not None and st.button("Rate outfit"):
        with st.spinner("Rating…"):
            result = rate_outfit(embedder, rate_img)
        st.metric("Style score", f"{result['rating']} / 10")
        st.progress(result["rating"] / 10.0)
        st.write(f"**Assessment:** {result['label']}")
        with st.expander("Score breakdown"):
            st.json(result["breakdown"])
