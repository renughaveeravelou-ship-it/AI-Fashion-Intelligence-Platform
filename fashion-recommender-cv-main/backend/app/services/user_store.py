"""Per-user style profile (likes, dislikes, embedding) — mirrors Streamlit personalization."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np

from backend.app.config import settings


def _conn():
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                liked_paths TEXT DEFAULT '[]',
                disliked_paths TEXT DEFAULT '[]',
                style_embedding TEXT,
                chat_history TEXT DEFAULT '[]',
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )


def get_profile(user_id: int) -> dict:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row is None:
            c.execute("INSERT INTO user_profiles (user_id) VALUES (?)", (user_id,))
            return {
                "liked_paths": [],
                "disliked_paths": [],
                "style_embedding": None,
                "chat_history": [],
            }
        return {
            "liked_paths": json.loads(row["liked_paths"] or "[]"),
            "disliked_paths": json.loads(row["disliked_paths"] or "[]"),
            "style_embedding": json.loads(row["style_embedding"]) if row["style_embedding"] else None,
            "chat_history": json.loads(row["chat_history"] or "[]"),
        }


def save_profile(user_id: int, profile: dict):
    with _conn() as c:
        c.execute(
            """
            UPDATE user_profiles SET
                liked_paths = ?, disliked_paths = ?,
                style_embedding = ?, chat_history = ?
            WHERE user_id = ?
            """,
            (
                json.dumps(profile["liked_paths"]),
                json.dumps(profile["disliked_paths"]),
                json.dumps(profile["style_embedding"]) if profile["style_embedding"] else None,
                json.dumps(profile["chat_history"]),
                user_id,
            ),
        )


def blend_with_profile(query_embedding: list[float], profile: dict, alpha: float = 0.75) -> list[float]:
    if profile.get("style_embedding") is None:
        return query_embedding
    query = np.array(query_embedding, dtype=np.float32)
    profile_vec = np.array(profile["style_embedding"], dtype=np.float32)
    mixed = alpha * query + (1 - alpha) * profile_vec
    mixed = mixed / (np.linalg.norm(mixed) + 1e-8)
    return mixed.tolist()


def filter_disliked(paths: list[str], profile: dict) -> list[str]:
    disliked = set(profile.get("disliked_paths", []))
    return [p for p in paths if p not in disliked]


def record_like(user_id: int, path: str, embedding: list[float] | None):
    profile = get_profile(user_id)
    if path not in profile["liked_paths"]:
        profile["liked_paths"].append(path)
    if path in profile["disliked_paths"]:
        profile["disliked_paths"].remove(path)
    if embedding is not None:
        vec = np.array(embedding, dtype=np.float32)
        if profile["style_embedding"] is None:
            profile["style_embedding"] = vec.tolist()
        else:
            current = np.array(profile["style_embedding"], dtype=np.float32)
            blended = 0.75 * current + 0.25 * vec
            profile["style_embedding"] = (blended / (np.linalg.norm(blended) + 1e-8)).tolist()
    save_profile(user_id, profile)


def record_dislike(user_id: int, path: str):
    profile = get_profile(user_id)
    if path not in profile["disliked_paths"]:
        profile["disliked_paths"].append(path)
    if path in profile["liked_paths"]:
        profile["liked_paths"].remove(path)
    save_profile(user_id, profile)
