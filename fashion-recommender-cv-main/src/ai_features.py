"""Advanced AI feature implementations for Smart Stylist."""

from __future__ import annotations

import os
import re
import tempfile
from collections import Counter
from datetime import datetime
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageEnhance

from src.personalization import blend_with_profile, filter_disliked
from src.utilities import extract_img_clip, similar_img_search_chroma

STYLE_PROMPTS = [
    "casual everyday outfit",
    "formal business attire",
    "sporty athletic wear",
    "vintage retro fashion",
    "minimalist modern style",
    "streetwear urban look",
    "bohemian eclectic outfit",
    "elegant evening wear",
]

COLOR_NAMES = [
    "black",
    "white",
    "red",
    "blue",
    "green",
    "yellow",
    "pink",
    "purple",
    "brown",
    "gray",
    "orange",
    "beige",
]

RATING_PROMPTS = [
    ("Poorly styled outfit", 2),
    ("Average everyday outfit", 5),
    ("Well coordinated stylish outfit", 8),
    ("High fashion editorial look", 10),
]

TREND_SEASONS = {
    "Spring": ["floral", "light", "pastel", "linen", "dress"],
    "Summer": ["shorts", "swim", "sandal", "bright", "tank"],
    "Fall": ["coat", "layer", "boot", "warm", "jacket"],
    "Winter": ["coat", "wool", "knit", "boot", "scarf"],
}


def unpack_detections(cropped_objects):
    if not cropped_objects:
        return [], []
    if isinstance(cropped_objects[0], tuple):
        crops, labels = zip(*cropped_objects)
        return list(crops), list(labels)
    return cropped_objects, ["Unknown"] * len(cropped_objects)


def multimodal_embedding(embedder, text: str | None, image_array: np.ndarray | None, text_weight: float = 0.5):
    parts = []
    if text and text.strip():
        parts.append((embedder.embed_text(text.strip()), text_weight))
    if image_array is not None:
        parts.append((embedder.embed_image(image_array), 1.0 - text_weight))
    if not parts:
        return None
    total_w = sum(w for _, w in parts)
    vec = np.zeros(len(parts[0][0]), dtype=np.float32)
    for emb, w in parts:
        vec += (w / total_w) * np.array(emb, dtype=np.float32)
    vec = vec / (np.linalg.norm(vec) + 1e-8)
    return vec.tolist()


def search_similar(
    embedder,
    collection,
    query_embedding: list[float],
    n_results: int = 6,
    where=None,
    personalized: bool = True,
):
    embedding = blend_with_profile(query_embedding) if personalized else query_embedding
    paths = similar_img_search_chroma(embedding, collection, n_results=n_results * 2, where=where)
    paths = filter_disliked(paths)
    return paths[:n_results]


def detect_attributes(embedder, image_array: np.ndarray, yolo_label: str = "Unknown") -> dict[str, Any]:
    pil = Image.fromarray(image_array).convert("RGB")
    dominant_color = _dominant_color_name(image_array)
    style_scores = _clip_zero_shot(embedder, pil, STYLE_PROMPTS)
    top_style = max(style_scores, key=style_scores.get)
    pattern = _estimate_pattern(image_array)
    return {
        "category": yolo_label,
        "dominant_color": dominant_color,
        "style": top_style,
        "pattern": pattern,
        "style_scores": style_scores,
    }


def _dominant_color_name(image_array: np.ndarray) -> str:
    small = Image.fromarray(image_array).convert("RGB").resize((64, 64))
    pixels = np.array(small).reshape(-1, 3).astype(np.float32)
    mean = pixels.mean(axis=0)
    palette = {
        "black": np.array([30, 30, 30]),
        "white": np.array([230, 230, 230]),
        "red": np.array([180, 40, 40]),
        "blue": np.array([40, 80, 180]),
        "green": np.array([40, 140, 60]),
        "yellow": np.array([220, 200, 40]),
        "pink": np.array([220, 120, 150]),
        "purple": np.array([120, 60, 160]),
        "brown": np.array([120, 80, 50]),
        "gray": np.array([128, 128, 128]),
        "orange": np.array([220, 120, 40]),
        "beige": np.array([210, 190, 160]),
    }
    return min(palette, key=lambda c: np.linalg.norm(mean - palette[c]))


def _estimate_pattern(image_array: np.ndarray) -> str:
    gray = np.mean(image_array, axis=2)
    grad = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
    if grad > 35:
        return "patterned / textured"
    if grad > 18:
        return "subtle texture"
    return "solid"


def _clip_zero_shot(embedder, pil_image: Image.Image, prompts: list[str]) -> dict[str, float]:
    img_emb = np.array(embedder.embed_image(np.array(pil_image)), dtype=np.float32)
    scores = {}
    for prompt in prompts:
        txt_emb = np.array(embedder.embed_text(prompt), dtype=np.float32)
        scores[prompt] = float(np.dot(img_emb, txt_emb))
    return scores


def caption_image(processor, model, image_array: np.ndarray) -> str:
    pil = Image.fromarray(image_array).convert("RGB")
    inputs = processor(pil, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=40)
    return processor.decode(out[0], skip_special_tokens=True)


def rate_outfit(embedder, image_array: np.ndarray) -> dict[str, Any]:
    pil = Image.fromarray(image_array).convert("RGB")
    scores = {}
    for prompt, base in RATING_PROMPTS:
        sim = _clip_zero_shot(embedder, pil, [prompt])[prompt]
        scores[prompt] = sim
    weighted = sum(scores[p] * b for p, b in RATING_PROMPTS.items())
    norm = sum(scores.values()) + 1e-8
    rating = max(1.0, min(10.0, weighted / norm))
    best_label = max(scores, key=scores.get)
    return {"rating": round(rating, 1), "label": best_label, "breakdown": scores}


def predict_trends(collection, sample_size: int = 500) -> dict[str, Any]:
    try:
        data = collection.get(limit=sample_size, include=["metadatas"])
    except Exception:
        return {"categories": {}, "season_hints": {}, "total": 0}

    metas = data.get("metadatas") or []
    categories = Counter()
    season_hits = Counter()
    for meta in metas:
        if not meta:
            continue
        cat = meta.get("category", "Unknown")
        categories[cat] += 1
        path = meta.get("path", "").lower()
        for season, keywords in TREND_SEASONS.items():
            if any(k in path or k in cat.lower() for k in keywords):
                season_hits[season] += 1

    month = datetime.now().month
    current_season = (
        "Winter" if month in (12, 1, 2) else "Spring" if month in (3, 4, 5) else "Summer" if month in (6, 7, 8) else "Fall"
    )
    top_cats = categories.most_common(8)
    return {
        "categories": dict(top_cats),
        "season_hints": dict(season_hits),
        "current_season": current_season,
        "total": len(metas),
        "rising": [c for c, _ in top_cats[:3]],
    }


def virtual_try_on(person_image: np.ndarray, garment_image: np.ndarray, region: str = "torso") -> np.ndarray:
    person = Image.fromarray(person_image).convert("RGBA")
    garment = Image.fromarray(garment_image).convert("RGBA")

    pw, ph = person.size
    if region == "lower":
        box = (int(pw * 0.2), int(ph * 0.45), int(pw * 0.8), int(ph * 0.95))
    elif region == "full":
        box = (int(pw * 0.15), int(ph * 0.1), int(pw * 0.85), int(ph * 0.9))
    else:
        box = (int(pw * 0.15), int(ph * 0.15), int(pw * 0.85), int(ph * 0.55))

    x1, y1, x2, y2 = box
    target_w, target_h = x2 - x1, y2 - y1
    garment = garment.resize((target_w, target_h), Image.Resampling.LANCZOS)
    garment = ImageEnhance.Brightness(garment).enhance(1.05)

    alpha = garment.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.72)
    garment.putalpha(alpha)

    composite = person.copy()
    composite.paste(garment, (x1, y1), garment)
    return np.array(composite.convert("RGB"))


def transcribe_audio(audio_bytes: bytes) -> str | None:
    try:
        import speech_recognition as sr
    except ImportError:
        return None

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception:
        return None
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def chatbot_reply(
    user_message: str,
    embedder,
    collection,
    yolo,
    chat_history: list[dict],
) -> tuple[str, list[str]]:
    msg = user_message.strip().lower()
    if not msg:
        return "Ask me about outfits, trends, colors, or upload a look to discuss.", []

    greetings = ("hi", "hello", "hey", "help")
    if any(msg.startswith(g) for g in greetings):
        return (
            "I'm your AI fashion assistant. Try:\n"
            "- *Find a red floral dress*\n"
            "- *What's trending this season?*\n"
            "- *Rate my outfit* (upload on Home first)\n"
            "- *Casual summer outfit ideas*",
            [],
        )

    if "trend" in msg or "season" in msg or "popular" in msg:
        trends = predict_trends(collection)
        season = trends["current_season"]
        rising = ", ".join(trends["rising"][:3]) or "Dresses, Shirts, Pants"
        reply = (
            f"For **{season}**, popular categories in our catalog include **{rising}**. "
            f"I analyzed {trends['total']} indexed items. Use **Fashion Trend Prediction** for charts."
        )
        return reply, []

    search_text = user_message
    for prefix in ("find", "search", "show me", "recommend", "i want", "looking for"):
        if msg.startswith(prefix):
            search_text = user_message[len(prefix) :].strip(" :,-")
            break

    embedding = embedder.embed_text(search_text or user_message)
    paths = search_similar(embedder, collection, embedding, n_results=4)
    if paths:
        reply = f"Here are items matching **{search_text or user_message}**. I found {len(paths)} similar looks in our catalog."
    else:
        reply = "I couldn't find close matches. Try broader terms like 'blue dress' or 'casual sneakers'."

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": reply})
    return reply, paths


def advanced_ensemble_search(embedder, collection, yolo, image_array, text: str | None, where=None):
    crops, labels = unpack_detections(yolo.crop_objects(image_array))
    embeddings = []
    if text:
        embeddings.append(np.array(embedder.embed_text(text), dtype=np.float32))
    for crop in crops:
        if crop.size > 0:
            embeddings.append(np.array(extract_img_clip(crop, embedder), dtype=np.float32))
    if not embeddings:
        emb = multimodal_embedding(embedder, text, image_array)
        if emb:
            paths = search_similar(embedder, collection, emb, where=where)
            return paths, []
        return [], []

    fused = np.mean(embeddings, axis=0)
    fused = fused / (np.linalg.norm(fused) + 1e-8)
    paths = search_similar(embedder, collection, fused.tolist(), where=where)
    attrs = [detect_attributes(embedder, c, lbl) for c, lbl in zip(crops, labels)] if crops else []
    return paths, attrs
