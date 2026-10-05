"""Yandex OAuth2 Authorization Code helpers (server-side only)."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from core.errors import AppError, UnauthorizedError, ValidationError

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"


@dataclass(frozen=True)
class YandexOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str

    @classmethod
    def from_env(cls) -> YandexOAuthConfig | None:
        client_id = os.getenv("YANDEX_CLIENT_ID", "").strip()
        client_secret = os.getenv("YANDEX_CLIENT_SECRET", "").strip()
        api_public = os.getenv("OAUTH_API_PUBLIC_URL", "http://127.0.0.1:5001").strip().rstrip("/")
        if not client_id or not client_secret:
            return None
        if client_id.startswith("your_") or client_secret.startswith("your_"):
            return None
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=f"{api_public}/api/auth/oauth/yandex/callback",
        )


@dataclass(frozen=True)
class YandexUserInfo:
    yandex_id: str
    email: str
    display_name: str | None


def new_oauth_state() -> str:
    return secrets.token_urlsafe(24)


def build_yandex_authorize_url(config: YandexOAuthConfig, state: str) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "state": state,
            "force_confirm": "yes",
        }
    )
    return f"{YANDEX_AUTH_URL}?{query}"


def exchange_yandex_code(config: YandexOAuthConfig, code: str) -> str:
    """Exchange auth code for Yandex access token."""
    try:
        response = httpx.post(
            YANDEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": config.client_id,
                "client_secret": config.client_secret,
            },
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise AppError(code="INTERNAL_ERROR", status_code=502, message="Yandex token exchange failed") from exc

    if response.status_code >= 400:
        raise UnauthorizedError(code="UNAUTHORIZED")

    data = response.json()
    token = str(data.get("access_token") or "").strip()
    if not token:
        raise UnauthorizedError(code="UNAUTHORIZED")
    return token


def fetch_yandex_user(access_token: str) -> YandexUserInfo:
    try:
        response = httpx.get(
            YANDEX_USERINFO_URL,
            params={"format": "json"},
            headers={"Authorization": f"OAuth {access_token}"},
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise AppError(code="INTERNAL_ERROR", status_code=502, message="Yandex userinfo failed") from exc

    if response.status_code >= 400:
        raise UnauthorizedError(code="UNAUTHORIZED")

    data: dict[str, Any] = response.json()
    yandex_id = str(data.get("id") or "").strip()
    email = str(data.get("default_email") or data.get("emails", [None])[0] or "").strip()
    if not email and data.get("login"):
        email = f"{data['login']}@yandex.ru"
    display = str(data.get("display_name") or data.get("real_name") or "").strip() or None
    if not yandex_id or not email:
        raise ValidationError(code="VALIDATION_ERROR", message="Yandex profile missing id/email")
    return YandexUserInfo(yandex_id=yandex_id, email=email.lower(), display_name=display)
