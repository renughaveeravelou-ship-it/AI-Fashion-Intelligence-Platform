from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.services.auth_service import decode_token

security = HTTPBearer(auto_error=False)


def get_optional_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> int | None:
    if not creds:
        return None
    payload = decode_token(creds.credentials)
    if not payload:
        return None
    return int(payload["sub"])


def get_required_user(user_id: int | None = Depends(get_optional_user)) -> int:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id
