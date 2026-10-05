"""Google OAuth2 Authorization Code helpers (server-side only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from core.errors import AppError, UnauthorizedError, ValidationError
from integrations.oauth_yandex import new_oauth_state

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@dataclass(frozen=True)
class GoogleOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str

    @classmethod
    def from_env(cls) -> GoogleOAuthConfig | None:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        api_public = os.getenv("OAUTH_API_PUBLIC_URL", "http://127.0.0.1:5001").strip().rstrip("/")
        if not client_id or not client_secret:
            return None
        if client_id.startswith("your_") or client_secret.startswith("your_"):
            return None
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=f"{api_public}/api/auth/oauth/google/callback",
        )


@dataclass(frozen=True)
class GoogleUserInfo:
    google_id: str
    email: str
    display_name: str | None


def build_google_authorize_url(config: GoogleOAuthConfig, state: str) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_google_code(config: GoogleOAuthConfig, code: str) -> str:
    try:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "redirect_uri": config.redirect_uri,
            },
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise AppError(code="INTERNAL_ERROR", status_code=502, message="Google token exchange failed") from exc

    if response.status_code >= 400:
        raise UnauthorizedError(code="UNAUTHORIZED")

    token = str(response.json().get("access_token") or "").strip()
    if not token:
        raise UnauthorizedError(code="UNAUTHORIZED")
    return token


def fetch_google_user(access_token: str) -> GoogleUserInfo:
    try:
        response = httpx.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise AppError(code="INTERNAL_ERROR", status_code=502, message="Google userinfo failed") from exc

    if response.status_code >= 400:
        raise UnauthorizedError(code="UNAUTHORIZED")

    data: dict[str, Any] = response.json()
    google_id = str(data.get("sub") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    display = str(data.get("name") or "").strip() or None
    if not google_id or not email:
        raise ValidationError(code="VALIDATION_ERROR", message="Google profile missing sub/email")
    return GoogleUserInfo(google_id=google_id, email=email, display_name=display)


# re-export for callers that import state helper from google module
__all__ = [
    "GoogleOAuthConfig",
    "GoogleUserInfo",
    "build_google_authorize_url",
    "exchange_google_code",
    "fetch_google_user",
    "new_oauth_state",
]
