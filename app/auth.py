"""Supabase JWT verification for Flask middleware."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from jwt import InvalidTokenError

from core.errors import UnauthorizedError


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    role: str | None = None
    email: str | None = None


def _jwt_secret() -> str | None:
    secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
    return secret or None


def _supabase_url() -> str | None:
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    return url or None


def _anon_key() -> str | None:
    key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    return key or None


def verify_supabase_access_token(token: str) -> AuthUser:
    """
    Verify a Supabase Auth access token.

    Preference order:
    1. Local HS256 verify with SUPABASE_JWT_SECRET (no network)
    2. Supabase Auth `/user` endpoint (needs SUPABASE_URL + SUPABASE_ANON_KEY)
    """
    token = token.strip()
    if not token:
        raise UnauthorizedError()

    secret = _jwt_secret()
    if secret:
        return _verify_locally(token, secret)

    url = _supabase_url()
    anon = _anon_key()
    if url and anon:
        return _verify_via_auth_api(token, url, anon)

    raise UnauthorizedError(code="UNAUTHORIZED")


def _verify_locally(token: str, secret: str) -> AuthUser:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["sub", "exp"]},
        )
    except InvalidTokenError as exc:
        raise UnauthorizedError() from exc

    user_id = str(payload.get("sub") or "").strip()
    if not user_id:
        raise UnauthorizedError()

    return AuthUser(
        user_id=user_id,
        role=str(payload.get("role")) if payload.get("role") else None,
        email=str(payload.get("email")) if payload.get("email") else None,
    )


def _verify_via_auth_api(token: str, supabase_url: str, anon_key: str) -> AuthUser:
    try:
        response = httpx.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": anon_key,
            },
            timeout=8.0,
        )
    except httpx.HTTPError as exc:
        raise UnauthorizedError() from exc

    if response.status_code != 200:
        raise UnauthorizedError()

    data = response.json()
    user_id = str(data.get("id") or "").strip()
    if not user_id:
        raise UnauthorizedError()

    return AuthUser(
        user_id=user_id,
        email=str(data.get("email")) if data.get("email") else None,
        role="authenticated",
    )


def mint_test_access_token(
    *,
    user_id: str,
    secret: str,
    email: str = "test@example.com",
    expires_seconds: int = 3600,
) -> str:
    """Create an HS256 access token shaped like Supabase Auth (tests only)."""
    import time

    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iat": now,
        "exp": now + expires_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")
