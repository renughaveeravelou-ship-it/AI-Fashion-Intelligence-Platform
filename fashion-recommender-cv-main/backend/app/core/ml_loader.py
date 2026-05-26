"""Singleton ML model loader (no Streamlit dependency)."""

from __future__ import annotations


class MLModels:
    _loaded = False
    yolo = None
    embedder = None
    collection = None
    caption_processor = None
    caption_model = None

    @classmethod
    def load(cls):
        if cls._loaded:
            return cls
        from obj_detection import ObjDetection
        from src.utilities import FashionCLIPEmbedder, get_chroma_collection

        cls.yolo = ObjDetection(
            onnx_model="./models/best.onnx",
            data_yaml="./models/data.yaml",
        )
        cls.embedder = FashionCLIPEmbedder()
        cls.collection = get_chroma_collection()
        cls._loaded = True
        return cls

    @classmethod
    def load_caption(cls):
        cls.load()
        if cls.caption_model is None:
            from transformers import BlipForConditionalGeneration, BlipProcessor

            name = "Salesforce/blip-image-captioning-base"
            cls.caption_processor = BlipProcessor.from_pretrained(name)
            cls.caption_model = BlipForConditionalGeneration.from_pretrained(name)
            cls.caption_model.eval()
        return cls.caption_processor, cls.caption_model
