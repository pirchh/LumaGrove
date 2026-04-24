from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import require_admin
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import AdminMeResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    username_ok = hmac.compare_digest(payload.username, settings.admin_username)
    password_ok = hmac.compare_digest(payload.password, settings.admin_password)
    if not username_ok or not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    return TokenResponse(access_token=create_access_token(subject=settings.admin_username))


@router.get("/me", response_model=AdminMeResponse)
def me(username: str = Depends(require_admin)) -> AdminMeResponse:
    return AdminMeResponse(username=username, is_admin=True)
