from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from backend.app.dependencies import get_optional_user
from backend.app.services import ai_service, user_store

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/search/text")
def search_text(
    query: str = Form(...),
    category: str = Form("All"),
    user_id: int | None = Depends(get_optional_user),
):
    return {"items": ai_service.text_search(query, category, user_id=user_id)}


@router.post("/search/image")
async def search_image(
    file: UploadFile = File(...),
    category: str = Form("All"),
    user_id: int | None = Depends(get_optional_user),
):
    data = await file.read()
    return ai_service.image_search(data, category, user_id=user_id)


@router.post("/search/multimodal")
async def search_multimodal(
    text: str = Form(""),
    text_weight: float = Form(0.5),
    category: str = Form("All"),
    file: UploadFile | None = File(None),
    user_id: int | None = Depends(get_optional_user),
):
    img = await file.read() if file else None
    items = ai_service.multimodal_search(text or None, img, text_weight, category, user_id)
    return {"items": items}


@router.post("/advanced")
async def advanced(
    file: UploadFile = File(...),
    text: str = Form(""),
    category: str = Form("All"),
    user_id: int | None = Depends(get_optional_user),
):
    return ai_service.advanced_ai(text or None, await file.read(), category, user_id)


@router.post("/try-on")
async def try_on(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
    region: str = Form("torso"),
):
    b64 = ai_service.try_on(await person.read(), await garment.read(), region)
    return {"image_base64": b64}


@router.post("/chat")
def chat(
    message: str = Form(...),
    user_id: int | None = Depends(get_optional_user),
):
    return ai_service.chat(message, user_id)


@router.get("/trends")
def trends():
    return ai_service.trends()


@router.post("/attributes")
async def attributes(file: UploadFile = File(...)):
    return {"attributes": ai_service.attributes(await file.read())}


@router.post("/caption")
async def caption(file: UploadFile = File(...)):
    cap = ai_service.caption(await file.read())
    return {"caption": cap}


@router.post("/rate")
async def rate(file: UploadFile = File(...)):
    return ai_service.rating(await file.read())


@router.post("/voice")
async def voice(
    file: UploadFile = File(...),
    category: str = Form("All"),
    user_id: int | None = Depends(get_optional_user),
):
    return ai_service.voice_search(await file.read(), category, user_id)


@router.post("/personalized")
def personalized(
    query: str = Form(...),
    category: str = Form("All"),
    personalized: bool = Form(True),
    user_id: int | None = Depends(get_optional_user),
):
    return {
        "items": ai_service.text_search(
            query, category, user_id=user_id, personalized=personalized
        ),
        "profile_active": bool(
            user_id and user_store.get_profile(user_id).get("style_embedding")
        ),
    }


@router.post("/feedback/like")
def like_item(
    path: str = Form(...),
    user_id: int | None = Depends(get_optional_user),
):
    if not user_id:
        return {"ok": False, "message": "Sign in to save preferences"}
    from backend.app.core.ml_loader import MLModels
    import os
    from PIL import Image
    import numpy as np

    ml = MLModels.load()
    emb = None
    if os.path.exists(path):
        img = np.array(Image.open(path).convert("RGB"))
        emb = ml.embedder.embed_image(img)
    user_store.record_like(user_id, path, emb)
    return {"ok": True}


@router.post("/feedback/dislike")
def dislike_item(path: str = Form(...), user_id: int | None = Depends(get_optional_user)):
    if not user_id:
        return {"ok": False}
    user_store.record_dislike(user_id, path)
    return {"ok": True}
