"""Shared model and database loaders for the Streamlit app."""

import streamlit as st

from obj_detection import ObjDetection
from src.utilities import FashionCLIPEmbedder, get_chroma_collection


@st.cache_resource
def load_yolo():
    return ObjDetection(
        onnx_model="./models/best.onnx",
        data_yaml="./models/data.yaml",
    )


@st.cache_resource
def load_embedder_and_db():
    embedder = FashionCLIPEmbedder()
    collection = get_chroma_collection()
    return embedder, collection


@st.cache_resource
def load_caption_model():
    from transformers import BlipForConditionalGeneration, BlipProcessor

    model_name = "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained(model_name)
    model = BlipForConditionalGeneration.from_pretrained(model_name)
    model.eval()
    return processor, model
