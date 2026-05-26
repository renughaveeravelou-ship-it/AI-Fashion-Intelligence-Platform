from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.ml_loader import MLModels
from backend.app.dependencies import get_optional_user
from backend.app.services import ai_service, user_store

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(user_id: int | None = Depends(get_optional_user)):
    ml = MLModels.load()
    count = ml.collection.count()
    profile = user_store.get_profile(user_id) if user_id else {}
    trends = ai_service.trends()
    return {
        "catalog_size": count,
        "liked_count": len(profile.get("liked_paths", [])),
        "profile_active": bool(profile.get("style_embedding")),
        "current_season": trends.get("current_season"),
        "rising_categories": trends.get("rising", []),
        "ai_features": [
            "Advanced AI",
            "Virtual Try-On",
            "Fashion Chatbot",
            "Trend Prediction",
            "Smart Attributes",
            "Personalized Engine",
            "Voice Search",
            "Image Captioning",
            "Multi-Modal Search",
            "Fashion Rating",
        ],
    }


@router.get("/themes")
def themes():
    return {
        "themes": [
            {"id": "aurora", "name": "Aurora", "primary": "#8b5cf6", "accent": "#ec4899"},
            {"id": "midnight", "name": "Midnight", "primary": "#3b82f6", "accent": "#06b6d4"},
            {"id": "luxury", "name": "Luxury", "primary": "#d4af37", "accent": "#1a1a2e"},
            {"id": "forest", "name": "Forest", "primary": "#10b981", "accent": "#84cc16"},
            {"id": "sunset", "name": "Sunset", "primary": "#f97316", "accent": "#ef4444"},
        ]
    }
