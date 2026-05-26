from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from backend.app.config import PROJECT_ROOT
from backend.app.services import ai_service

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


def _safe_path(rel: str) -> Path:
    decoded = unquote(rel).replace("/", os.sep).lstrip(os.sep)
    full = (PROJECT_ROOT / decoded).resolve()
    if not str(full).startswith(str(PROJECT_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Invalid path")
    if not full.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return full


@router.get("/image")
def serve_image(path: str = Query(...)):
    return FileResponse(_safe_path(path))


@router.get("/feed")
def feed(limit: int = 48):
    return {"items": ai_service.catalog_sample(limit)}
