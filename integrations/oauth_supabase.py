"""Create / sign-in Supabase Auth users for OAuth providers (service role)."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from typing import Any

import httpx

from core.errors import AppError, UnauthorizedError


@dataclass(frozen=True)
class SupabaseSessionTokens:
    access_token: str
    refresh_token: str
    user_id: str
    email: str


def _supabase_url() -> str:
    return (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")


def _service_role() -> str:
    return (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()


def _anon_key() -> str:
    return (os.getenv("SUPABASE_ANON_KEY") or "").strip()


def service_role_configured() -> bool:
    key = _service_role()
    return bool(_supabase_url() and key and not key.startswith("your_"))


def upsert_oauth_user_and_session(
    *,
    email: str,
    provider: str,
    provider_user_id: str,
    display_name: str | None = None,
) -> SupabaseSessionTokens:
    """
    Ensure auth user exists, set a one-time password, exchange for session tokens.

    Requires SUPABASE_SERVICE_ROLE_KEY (server-only).
    """
    if not service_role_configured():
        raise AppError(
            code="INTERNAL_ERROR",
            status_code=503,
            message="SUPABASE_SERVICE_ROLE_KEY is not configured for OAuth sign-in",
        )

    base = _supabase_url()
    service = _service_role()
    anon = _anon_key() or service
    password = secrets.token_urlsafe(32)
    headers = {
        "Authorization": f"Bearer {service}",
        "apikey": service,
        "Content-Type": "application/json",
    }
    metadata = {
        "provider": provider,
        "providers": [provider],
        f"{provider}_id": provider_user_id,
    }
    user_meta: dict[str, Any] = {
        "full_name": display_name or email,
        "name": display_name or email,
        "provider": provider,
        f"{provider}_id": provider_user_id,
    }

    # Try create; on conflict (422) look up and update password.
    create = httpx.post(
        f"{base}/auth/v1/admin/users",
        headers=headers,
        json={
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": user_meta,
            "app_metadata": metadata,
        },
        timeout=20.0,
    )
    user_id: str | None = None
    if create.status_code < 300:
        user_id = str(create.json().get("id") or "").strip() or None
    else:
        listed = httpx.get(
            f"{base}/auth/v1/admin/users",
            headers=headers,
            params={"page": 1, "per_page": 200},
            timeout=20.0,
        )
        if listed.status_code >= 400:
            raise AppError(code="INTERNAL_ERROR", status_code=502, message="Supabase admin list users failed")
        users = listed.json().get("users") or []
        match = next((u for u in users if str(u.get("email", "")).lower() == email.lower()), None)
        if match is None:
            raise AppError(
                code="INTERNAL_ERROR",
                status_code=502,
                message=f"Cannot create/find OAuth user ({create.status_code})",
            )
        user_id = str(match["id"])
        upd = httpx.put(
            f"{base}/auth/v1/admin/users/{user_id}",
            headers=headers,
            json={
                "password": password,
                "email_confirm": True,
                "user_metadata": {**(match.get("user_metadata") or {}), **user_meta},
                "app_metadata": {**(match.get("app_metadata") or {}), **metadata},
            },
            timeout=20.0,
        )
        if upd.status_code >= 400:
            raise AppError(code="INTERNAL_ERROR", status_code=502, message="Supabase admin update user failed")

    if not user_id:
        raise AppError(code="INTERNAL_ERROR", status_code=502, message="OAuth user id missing")

    token_res = httpx.post(
        f"{base}/auth/v1/token?grant_type=password",
        headers={"apikey": anon, "Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=20.0,
    )
    if token_res.status_code >= 400:
        raise UnauthorizedError(code="UNAUTHORIZED")

    body = token_res.json()
    access = str(body.get("access_token") or "").strip()
    refresh = str(body.get("refresh_token") or "").strip()
    if not access or not refresh:
        raise UnauthorizedError(code="UNAUTHORIZED")

    return SupabaseSessionTokens(
        access_token=access,
        refresh_token=refresh,
        user_id=user_id,
        email=email,
    )


def google_oauth_dashboard_hints() -> dict[str, str | bool]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    configured = bool(client_id and secret and not client_id.startswith("your_") and not secret.startswith("your_"))
    return {
        "provider": "google",
        "env_configured": configured,
        "note": "Enable Google in Supabase Dashboard → Authentication → Providers and paste the same Client ID/Secret",
    }
