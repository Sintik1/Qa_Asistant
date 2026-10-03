"""Auth / JWT / CORS contract for DZ step 5."""

from __future__ import annotations

import pytest

from app import create_app
from app.auth import mint_test_access_token, verify_supabase_access_token
from core.errors import UnauthorizedError
from core.messages import ERROR_MESSAGES

TEST_JWT_SECRET = "test-supabase-jwt-secret-for-unit-tests"
USER_ID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"


@pytest.fixture()
def jwt_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    monkeypatch.delenv("AUTH_DEV_BYPASS", raising=False)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    # Auth unit tests must not hit live PostgREST.
    monkeypatch.setenv("PERSIST_BACKEND", "memory")


@pytest.fixture()
def prod_client(jwt_env):
    """Non-testing app: X-User-Id must not bypass JWT."""
    return create_app(testing=False).test_client()


@pytest.fixture()
def test_client(jwt_env):
    return create_app(testing=True).test_client()


def test_verify_valid_token(jwt_env):
    token = mint_test_access_token(user_id=USER_ID, secret=TEST_JWT_SECRET)
    user = verify_supabase_access_token(token)
    assert user.user_id == USER_ID
    assert user.role == "authenticated"


def test_verify_invalid_token_raises(jwt_env):
    with pytest.raises(UnauthorizedError):
        verify_supabase_access_token("not.a.jwt")


def test_api_rejects_missing_auth_in_prod(prod_client):
    res = prod_client.get("/api/runs")
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "UNAUTHORIZED"
    assert res.get_json()["error"]["message"] == ERROR_MESSAGES["UNAUTHORIZED"]


def test_api_rejects_x_user_id_without_jwt_in_prod(prod_client):
    res = prod_client.get(
        "/api/runs",
        headers={"X-User-Id": USER_ID},
    )
    assert res.status_code == 401


def test_api_accepts_valid_supabase_jwt(prod_client):
    token = mint_test_access_token(user_id=USER_ID, secret=TEST_JWT_SECRET)
    res = prod_client.get(
        "/api/runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.get_json()["items"] == []


def test_api_rejects_tampered_jwt(prod_client):
    token = mint_test_access_token(user_id=USER_ID, secret=TEST_JWT_SECRET)
    bad = token[:-4] + "xxxx"
    res = prod_client.get(
        "/api/runs",
        headers={"Authorization": f"Bearer {bad}"},
    )
    assert res.status_code == 401


def test_testing_mode_still_allows_x_user_id(test_client):
    res = test_client.get(
        "/api/runs",
        headers={"X-User-Id": USER_ID},
    )
    assert res.status_code == 200


def test_health_remains_public(prod_client):
    assert prod_client.get("/api/health").status_code == 200


def test_cors_allows_configured_origin(prod_client):
    res = prod_client.options(
        "/api/runs",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert res.status_code in {200, 204}
    assert res.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_cors_blocks_unknown_origin(prod_client):
    res = prod_client.options(
        "/api/runs",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    # flask-cors omits Allow-Origin for disallowed origins
    assert res.headers.get("Access-Control-Allow-Origin") != "http://evil.example"
