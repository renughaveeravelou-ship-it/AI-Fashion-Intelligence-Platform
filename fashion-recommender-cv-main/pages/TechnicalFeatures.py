import streamlit as st

st.set_page_config(page_title="Technical Features", page_icon="🛍️")

st.markdown("# 🧚 Technical Features")
st.divider()

st.write(
    "Smart Stylist combines computer vision and multimodal AI for fashion discovery. "
    "The pipeline: **YOLO object detection** → **FashionCLIP embeddings** → **ChromaDB similarity search**."
)

st.image("images/flowcharts/serving_stg.png")
st.caption(
    "Query images are parsed into fashion objects; each object is embedded and matched against the catalog."
)

st.image("images/flowcharts/vector_index.png")
st.caption("Catalog items are indexed in ChromaDB with cosine similarity for fast retrieval.")

st.divider()
st.markdown("#### AI feature stack")
features = [
    "**Advanced AI** — YOLO + FashionCLIP ensemble with attribute fusion",
    "**Virtual try-on** — Garment overlay preview on user photos",
    "**Fashion chatbot** — Natural-language stylist with catalog search",
    "**Trend prediction** — Category and seasonal signals from the index",
    "**Smart attributes** — Color, pattern, category, and style detection",
    "**Personalized engine** — Session style profile from likes/dislikes",
    "**Voice search** — Speech-to-text fashion queries",
    "**Image captioning** — BLIP captions + similarity search",
    "**Multi-modal search** — Combined text + image embeddings",
    "**Fashion rating** — CLIP-based style scoring (1–10)",
]
for item in features:
    st.markdown(f"* {item}")

st.divider()
st.markdown("#### Model references")
st.markdown(
    "[Object Detection](https://www.joankusuma.com/post/object-detection-model-yolov5-on-fashion-images) · "
    "[Visual Search](https://www.joankusuma.com/post/powering-visual-search-with-image-embedding)"
)
