"""OAuth HTTP routes.

Primary Google login is FE → Supabase Auth Provider.
Yandex (+ optional legacy Google) use Flask Authorization Code → Supabase Admin session.
"""

from __future__ import annotations

import os
from urllib.parse import urlencode

from flask import Blueprint, g, jsonify, redirect, request

from core.errors import UnauthorizedError, ValidationError
from integrations.oauth_google import (
    GoogleOAuthConfig,
    build_google_authorize_url,
    exchange_google_code,
    fetch_google_user,
)
from integrations.oauth_supabase import service_role_configured, upsert_oauth_user_and_session
from integrations.oauth_yandex import (
    YandexOAuthConfig,
    build_yandex_authorize_url,
    exchange_yandex_code,
    fetch_yandex_user,
    new_oauth_state,
)

oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/auth")

# In-memory CSRF state (local / CI). Production: Redis / signed cookie.
_oauth_states: dict[str, str] = {}


def _fe_app_url() -> str:
    return os.getenv("OAUTH_PUBLIC_APP_URL", "http://127.0.0.1:5173").strip().rstrip("/")


def _redirect_fe_error(code: str, message: str):
    query = urlencode({"oauth_error": code, "oauth_message": message})
    return redirect(f"{_fe_app_url()}/auth/callback?{query}")


def _remember_state(provider: str) -> str:
    state = new_oauth_state()
    _oauth_states[state] = provider
    if len(_oauth_states) > 500:
        _oauth_states.clear()
        _oauth_states[state] = provider
    return state


def _finish_session(*, provider: str, email: str, provider_user_id: str, display_name: str | None):
    session = upsert_oauth_user_and_session(
        email=email,
        provider=provider,
        provider_user_id=provider_user_id,
        display_name=display_name,
    )
    fragment = urlencode(
        {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "provider": provider,
            "email": session.email,
            "user_id": session.user_id,
        }
    )
    return redirect(f"{_fe_app_url()}/auth/callback#{fragment}")


@oauth_bp.get("/oauth/status")
def oauth_status():
    """Which OAuth providers are ready (no secrets exposed)."""
    yandex = YandexOAuthConfig.from_env()
    google = GoogleOAuthConfig.from_env()
    supabase_url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    return jsonify(
        {
            "google": {
                # Primary FE path: supabase.auth.signInWithOAuth (Dashboard Providers).
                "flow": "supabase_auth_provider",
                "supabase_callback": (f"{supabase_url}/auth/v1/callback" if supabase_url else None),
                # Legacy Flask Google routes still available if GOOGLE_* set.
                "legacy_flask_env_configured": google is not None,
                "legacy_flask_redirect_uri": google.redirect_uri if google else None,
                "service_role_ready": service_role_configured(),
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


@oauth_bp.get("/oauth/google/start")
def google_start():
    config = GoogleOAuthConfig.from_env()
    if config is None:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message="Google OAuth is not configured (set GOOGLE_CLIENT_ID/SECRET in server .env)",
        )
    state = _remember_state("google")
    return redirect(build_google_authorize_url(config, state))


@oauth_bp.get("/oauth/google/callback")
def google_callback():
    err = (request.args.get("error") or "").strip()
    if err:
        return _redirect_fe_error("GOOGLE_DENIED", err)

    state = (request.args.get("state") or "").strip()
    code = (request.args.get("code") or "").strip()
    if not code or not state or _oauth_states.get(state) != "google":
        return _redirect_fe_error("GOOGLE_STATE", "Invalid OAuth state or code")
    _oauth_states.pop(state, None)

    config = GoogleOAuthConfig.from_env()
    if config is None:
        return _redirect_fe_error("GOOGLE_CONFIG", "Google OAuth is not configured")

    try:
        token = exchange_google_code(config, code)
        profile = fetch_google_user(token)
        return _finish_session(
            provider="google",
            email=profile.email,
            provider_user_id=profile.google_id,
            display_name=profile.display_name,
        )
    except UnauthorizedError:
        return _redirect_fe_error("GOOGLE_AUTH", "Google authorization failed")
    except Exception as exc:  # noqa: BLE001
        try:
            from infrastructure.logging_setup import get_logger

            get_logger().exception("google_oauth_failed")
        except Exception:  # noqa: BLE001
            pass
        return _redirect_fe_error("GOOGLE_ERROR", str(exc)[:180] or "OAuth failed")


@oauth_bp.get("/oauth/yandex/start")
def yandex_start():
    config = YandexOAuthConfig.from_env()
    if config is None:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message="Yandex OAuth is not configured (set YANDEX_CLIENT_ID/SECRET in server .env)",
        )
    state = _remember_state("yandex")
    return redirect(build_yandex_authorize_url(config, state))


@oauth_bp.get("/oauth/yandex/callback")
def yandex_callback():
    err = (request.args.get("error") or "").strip()
    if err:
        return _redirect_fe_error("YANDEX_DENIED", err)

    state = (request.args.get("state") or "").strip()
    code = (request.args.get("code") or "").strip()
    if not code or not state or _oauth_states.get(state) != "yandex":
        return _redirect_fe_error("YANDEX_STATE", "Invalid OAuth state or code")
    _oauth_states.pop(state, None)

    config = YandexOAuthConfig.from_env()
    if config is None:
        return _redirect_fe_error("YANDEX_CONFIG", "Yandex OAuth is not configured")

    try:
        yandex_token = exchange_yandex_code(config, code)
        profile = fetch_yandex_user(yandex_token)
        return _finish_session(
            provider="yandex",
            email=profile.email,
            provider_user_id=profile.yandex_id,
            display_name=profile.display_name,
        )
    except UnauthorizedError:
        return _redirect_fe_error("YANDEX_AUTH", "Yandex authorization failed")
    except Exception as exc:  # noqa: BLE001
        try:
            from infrastructure.logging_setup import get_logger

            get_logger().exception("yandex_oauth_failed")
        except Exception:  # noqa: BLE001
            pass
        return _redirect_fe_error("YANDEX_ERROR", str(exc)[:180] or "OAuth failed")


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
