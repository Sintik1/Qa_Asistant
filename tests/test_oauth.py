"""OAuth2 unit/API tests (mocked Yandex + Supabase admin)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app import create_app
from integrations.oauth_yandex import YandexUserInfo


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("YANDEX_CLIENT_ID", "test-yandex-client")
    monkeypatch.setenv("YANDEX_CLIENT_SECRET", "test-yandex-secret")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-google-client.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-google-secret")
    monkeypatch.setenv("OAUTH_API_PUBLIC_URL", "http://127.0.0.1:5001")
    monkeypatch.setenv("OAUTH_PUBLIC_APP_URL", "http://127.0.0.1:5173")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-test")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-test")
    application = create_app(testing=True)
    return application.test_client(), application


def test_oauth_status_reports_providers_configured(client):
    c, _ = client
    res = c.get("/api/auth/oauth/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["yandex"]["env_client_configured"] is True
    assert body["google"]["env_client_configured"] is True
    assert body["google"]["flow"] == "flask_authorization_code"
    assert "google/callback" in body["google"]["redirect_uri"]
    assert "yandex/callback" in body["yandex"]["redirect_uri"]


def test_google_start_redirects(client):
    c, _ = client
    res = c.get("/api/auth/oauth/google/start", follow_redirects=False)
    assert res.status_code in (302, 303)
    loc = res.headers["Location"]
    assert "accounts.google.com" in loc
    assert "client_id=test-google-client" in loc
    assert "state=" in loc


def test_yandex_start_redirects(client):
    c, _ = client
    res = c.get("/api/auth/oauth/yandex/start", follow_redirects=False)
    assert res.status_code in (302, 303)
    loc = res.headers["Location"]
    assert "oauth.yandex.ru/authorize" in loc
    assert "client_id=test-yandex-client" in loc
    assert "state=" in loc


def test_yandex_callback_invalid_state(client):
    c, _ = client
    res = c.get(
        "/api/auth/oauth/yandex/callback?code=abc&state=bad",
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    assert "oauth_error=YANDEX_STATE" in res.headers["Location"]


def test_yandex_callback_success_sets_fragment(client, monkeypatch):
    import app.oauth_routes as oauth_routes

    c, _ = client
    # Prime a valid state via start
    start = c.get("/api/auth/oauth/yandex/start", follow_redirects=False)
    from urllib.parse import parse_qs, urlparse

    state = parse_qs(urlparse(start.headers["Location"]).query)["state"][0]

    monkeypatch.setattr(
        oauth_routes,
        "exchange_yandex_code",
        lambda config, code: "yandex-access",
    )
    monkeypatch.setattr(
        oauth_routes,
        "fetch_yandex_user",
        lambda token: YandexUserInfo(
            yandex_id="42",
            email="user@yandex.ru",
            display_name="User",
        ),
    )
    monkeypatch.setattr(
        oauth_routes,
        "upsert_oauth_user_and_session",
        lambda **kwargs: MagicMock(
            access_token="acc",
            refresh_token="ref",
            email="user@yandex.ru",
            user_id="11111111-1111-4111-8111-111111111111",
        ),
    )

    res = c.get(
        f"/api/auth/oauth/yandex/callback?code=ok&state={state}",
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    loc = res.headers["Location"]
    assert loc.startswith("http://127.0.0.1:5173/auth/callback#")
    assert "access_token=acc" in loc
    assert "refresh_token=ref" in loc
    assert "provider=yandex" in loc


def test_auth_me_requires_user(client):
    c, _ = client
    denied = c.get("/api/auth/me", headers={"X-Skip-Auth": "1"})
    assert denied.status_code == 401

    ok = c.get("/api/auth/me", headers={"X-User-Id": "u-oauth-1"})
    assert ok.status_code == 200
    body = ok.get_json()
    assert body["user_id"] == "u-oauth-1"
    assert body["authenticated"] is True


def test_yandex_start_without_config(monkeypatch):
    monkeypatch.setenv("YANDEX_CLIENT_ID", "")
    monkeypatch.setenv("YANDEX_CLIENT_SECRET", "")
    app = create_app(testing=True)
    res = app.test_client().get("/api/auth/oauth/yandex/start")
    assert res.status_code == 422
