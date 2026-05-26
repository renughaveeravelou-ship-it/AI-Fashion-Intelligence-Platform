from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from backend.app.config import settings
from backend.app.services.user_store import _conn, init_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(email: str, username: str, password: str) -> dict:
    init_db()
    hashed = pwd_context.hash(password)
    with _conn() as c:
        try:
            cur = c.execute(
                "INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)",
                (email.lower(), username, hashed),
            )
            user_id = cur.lastrowid
            c.execute("INSERT INTO user_profiles (user_id) VALUES (?)", (user_id,))
        except Exception as e:
            if "UNIQUE" in str(e):
                raise ValueError("Email already registered") from e
            raise
    return {"id": user_id, "email": email.lower(), "username": username}


def authenticate(email: str, password: str) -> dict | None:
    init_db()
    with _conn() as c:
        row = c.execute(
            "SELECT id, email, username, hashed_password FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()
    if not row or not pwd_context.verify(password, row["hashed_password"]):
        return None
    return {"id": row["id"], "email": row["email"], "username": row["username"]}


def create_token(user: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user["id"]), "email": user["email"], "username": user["username"], "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
