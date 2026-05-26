from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from backend.app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterBody(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterBody):
    try:
        user = auth_service.register_user(body.email, body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    token = auth_service.create_token(user)
    return {"token": token, "user": user}


@router.post("/login")
def login(body: LoginBody):
    user = auth_service.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": auth_service.create_token(user), "user": user}
