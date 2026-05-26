"""AI service layer — wraps existing src/ai_features without breaking Streamlit."""

from __future__ import annotations

import base64
import io
from typing import Any
from urllib.parse import quote

import numpy as np
from PIL import Image

from backend.app.core.ml_loader import MLModels
from backend.app.services import user_store
from src.ai_features import (
    advanced_ensemble_search,
    caption_image,
    chatbot_reply,
    detect_attributes,
    multimodal_embedding,
    predict_trends,
    rate_outfit,
    transcribe_audio,
    unpack_detections,
    virtual_try_on,
)
from src.utilities import extract_img_clip, similar_img_search_chroma

CATEGORIES = ["All", "Shirts_&_Tops", "Dresses", "Pants", "Shoes", "Unknown"]


def _where(category: str | None):
    if not category or category == "All":
        return None
    return {"category": category}


def _load_image_bytes(data: bytes) -> np.ndarray:
    return np.array(Image.open(io.BytesIO(data)).convert("RGB"))


def _paths_to_items(paths: list[str]) -> list[dict]:
    items = []
    for p in paths:
        if p:
            items.append({
                "path": p,
                "url": f"/api/catalog/image?path={quote(p.replace(chr(92), '/'))}",
                "category": _category_from_path(p),
            })
    return items


def _category_from_path(path: str) -> str:
    import os
    base = os.path.basename(path)
    parts = base.split("_")
    if len(parts) > 2:
        return "_".join(parts[1:-1])
    return "Unknown"


def search_with_profile(
    embedding: list[float],
    category: str | None = None,
    n_results: int = 12,
    user_id: int | None = None,
    personalized: bool = True,
) -> list[dict]:
    ml = MLModels.load()
    where = _where(category)
    query_emb = embedding
    profile = None
    if user_id and personalized:
        profile = user_store.get_profile(user_id)
        query_emb = user_store.blend_with_profile(embedding, profile)
    paths = similar_img_search_chroma(query_emb, ml.collection, n_results=n_results * 2, where=where)
    if profile:
        paths = user_store.filter_disliked(paths, profile)
    return _paths_to_items(paths[:n_results])


def text_search(text: str, category: str | None = None, user_id: int | None = None, **kw) -> list[dict]:
    ml = MLModels.load()
    emb = ml.embedder.embed_text(text)
    return search_with_profile(emb, category, user_id=user_id, **kw)


def image_search(image_bytes: bytes, category: str | None = None, user_id: int | None = None, **kw) -> dict:
    ml = MLModels.load()
    img = _load_image_bytes(image_bytes)
    crops, labels = unpack_detections(ml.yolo.crop_objects(img))
    all_paths = []
    attrs = []
    for crop, label in zip(crops, labels):
        if crop.size > 0:
            emb = extract_img_clip(crop, ml.embedder)
            all_paths.extend(
                p["path"] for p in search_with_profile(emb, category, user_id=user_id, **kw)
            )
            attrs.append(detect_attributes(ml.embedder, crop, label))
    if not all_paths:
        emb = ml.embedder.embed_image(img)
        all_paths = [p["path"] for p in search_with_profile(emb, category, user_id=user_id, **kw)]
    return {"items": _paths_to_items(list(dict.fromkeys(all_paths))), "attributes": attrs}


def multimodal_search(
    text: str | None,
    image_bytes: bytes | None,
    text_weight: float = 0.5,
    category: str | None = None,
    user_id: int | None = None,
) -> list[dict]:
    ml = MLModels.load()
    img = _load_image_bytes(image_bytes) if image_bytes else None
    emb = multimodal_embedding(ml.embedder, text, img, text_weight=text_weight)
    if emb is None:
        return []
    return search_with_profile(emb, category, user_id=user_id)


def advanced_ai(text: str | None, image_bytes: bytes, category: str | None = None, user_id: int | None = None) -> dict:
    ml = MLModels.load()
    img = _load_image_bytes(image_bytes)
    paths, attrs = advanced_ensemble_search(
        ml.embedder, ml.collection, ml.yolo, img, text, where=_where(category)
    )
    if user_id:
        profile = user_store.get_profile(user_id)
        paths = user_store.filter_disliked(paths, profile)
    return {"items": _paths_to_items(paths), "attributes": attrs}


def try_on(person_bytes: bytes, garment_bytes: bytes, region: str = "torso") -> str:
    person = _load_image_bytes(person_bytes)
    garment = _load_image_bytes(garment_bytes)
    result = virtual_try_on(person, garment, region=region)
    img = Image.fromarray(result)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def attributes(image_bytes: bytes) -> list[dict]:
    ml = MLModels.load()
    img = _load_image_bytes(image_bytes)
    crops, labels = unpack_detections(ml.yolo.crop_objects(img))
    if not crops:
        return [detect_attributes(ml.embedder, img)]
    return [detect_attributes(ml.embedder, c, lbl) for c, lbl in zip(crops, labels) if c.size > 0]


def caption(image_bytes: bytes) -> str:
    ml = MLModels.load()
    processor, model = MLModels.load_caption()
    img = _load_image_bytes(image_bytes)
    return caption_image(processor, model, img)


def rating(image_bytes: bytes) -> dict:
    ml = MLModels.load()
    return rate_outfit(ml.embedder, _load_image_bytes(image_bytes))


def trends() -> dict:
    ml = MLModels.load()
    return predict_trends(ml.collection)


def chat(message: str, user_id: int | None = None) -> dict:
    ml = MLModels.load()
    history = []
    if user_id:
        history = user_store.get_profile(user_id)["chat_history"]
    reply, paths = chatbot_reply(message, ml.embedder, ml.collection, ml.yolo, history)
    if user_id:
        profile = user_store.get_profile(user_id)
        profile["chat_history"] = history[-20:]
        save = profile
        user_store.save_profile(user_id, save)
    return {"reply": reply, "items": _paths_to_items(paths)}


def voice_search(audio_bytes: bytes, category: str | None = None, user_id: int | None = None) -> dict:
    transcript = transcribe_audio(audio_bytes)
    if not transcript:
        return {"transcript": None, "items": [], "error": "Could not transcribe. Type your query or install SpeechRecognition."}
    items = text_search(transcript, category, user_id=user_id)
    return {"transcript": transcript, "items": items}


def catalog_sample(limit: int = 40) -> list[dict]:
    ml = MLModels.load()
    try:
        data = ml.collection.get(limit=limit, include=["metadatas"])
        metas = data.get("metadatas") or []
        paths = [m["path"] for m in metas if m and m.get("path")]
        return _paths_to_items(paths)
    except Exception:
        return []
