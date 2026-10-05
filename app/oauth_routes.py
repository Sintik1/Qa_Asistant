"""OAuth HTTP routes — thin handlers (Google via Supabase FE; Yandex via Flask)."""

from __future__ import annotations

import os
from urllib.parse import urlencode

from flask import Blueprint, g, jsonify, redirect, request

from core.errors import UnauthorizedError, ValidationError
from integrations.oauth_supabase import (
    google_oauth_dashboard_hints,
    service_role_configured,
    upsert_oauth_user_and_session,
)
from integrations.oauth_yandex import (
    YandexOAuthConfig,
    build_yandex_authorize_url,
    exchange_yandex_code,
    fetch_yandex_user,
    new_oauth_state,
)

oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/auth")

# In-memory CSRF state for Yandex (single-process local / CI). Production: Redis/signed cookie.
_oauth_states: set[str] = set()


def _fe_app_url() -> str:
    return os.getenv("OAUTH_PUBLIC_APP_URL", "http://127.0.0.1:5173").strip().rstrip("/")


def _redirect_fe_error(code: str, message: str):
    query = urlencode({"oauth_error": code, "oauth_message": message})
    return redirect(f"{_fe_app_url()}/auth/callback?{query}")


@oauth_bp.get("/oauth/status")
def oauth_status():
    """Which OAuth providers are ready (no secrets exposed)."""
    yandex = YandexOAuthConfig.from_env()
    google = google_oauth_dashboard_hints()
    return jsonify(
        {
            "google": {
                "env_client_configured": google["env_configured"],
                "flow": "supabase_fe_signInWithOAuth",
                "requires_supabase_dashboard": True,
            },
            "yandex": {
                "env_client_configured": yandex is not None,
                "flow": "flask_authorization_code",
                "redirect_uri": yandex.redirect_uri if yandex else None,
                "service_role_ready": service_role_configured(),
            },
            "frontend_callback": f"{_fe_app_url()}/auth/callback",
        }
    )


@oauth_bp.get("/oauth/yandex/start")
def yandex_start():
    config = YandexOAuthConfig.from_env()
    if config is None:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message="Yandex OAuth is not configured (set YANDEX_CLIENT_ID/SECRET in server .env)",
        )
    state = new_oauth_state()
    _oauth_states.add(state)
    # Cap memory growth in long-running process
    if len(_oauth_states) > 500:
        _oauth_states.clear()
        _oauth_states.add(state)
    return redirect(build_yandex_authorize_url(config, state))


@oauth_bp.get("/oauth/yandex/callback")
def yandex_callback():
    err = (request.args.get("error") or "").strip()
    if err:
        return _redirect_fe_error("YANDEX_DENIED", err)

    state = (request.args.get("state") or "").strip()
    code = (request.args.get("code") or "").strip()
    if not code or not state or state not in _oauth_states:
        return _redirect_fe_error("YANDEX_STATE", "Invalid OAuth state or code")
    _oauth_states.discard(state)

    config = YandexOAuthConfig.from_env()
    if config is None:
        return _redirect_fe_error("YANDEX_CONFIG", "Yandex OAuth is not configured")

    try:
        yandex_token = exchange_yandex_code(config, code)
        profile = fetch_yandex_user(yandex_token)
        session = upsert_oauth_user_and_session(
            email=profile.email,
            provider="yandex",
            provider_user_id=profile.yandex_id,
            display_name=profile.display_name,
        )
    except UnauthorizedError:
        return _redirect_fe_error("YANDEX_AUTH", "Yandex authorization failed")
    except Exception as exc:  # noqa: BLE001 — map to FE error page
        try:
            from infrastructure.logging_setup import get_logger

            get_logger().exception("yandex_oauth_failed")
        except Exception:  # noqa: BLE001
            pass
        return _redirect_fe_error("YANDEX_ERROR", str(exc)[:180] or "OAuth failed")

    # Pass tokens in URL fragment so they are not sent to server logs as Referer query.
    fragment = urlencode(
        {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "provider": "yandex",
            "email": session.email,
            "user_id": session.user_id,
        }
    )
    return redirect(f"{_fe_app_url()}/auth/callback#{fragment}")


@oauth_bp.get("/me")
def auth_me():
    """Current user from JWT (works for email + Google + Yandex sessions)."""
    if not getattr(g, "user_id", None):
        raise UnauthorizedError()
    return jsonify(
        {
            "user_id": g.user_id,
            "email": getattr(g, "user_email", None),
            "authenticated": True,
        }
    )
