"""Error contract: codes/messages align with TZ / frontend ERROR_MESSAGES."""

from __future__ import annotations

import pytest

from app import create_app
from core.messages import ERROR_MESSAGES


@pytest.fixture()
def client():
    return create_app(testing=True).test_client()


def test_unauthorized_without_user(client):
    res = client.get("/api/runs", headers={"X-Skip-Auth": "1"})
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"] == ERROR_MESSAGES["UNAUTHORIZED"]


def test_invalid_format(client):
    res = client.post(
        "/api/documents",
        json={"original_filename": "virus.exe", "size_bytes": 10},
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_FORMAT"
    assert res.get_json()["error"]["message"] == ERROR_MESSAGES["INVALID_FORMAT"]


def test_file_too_large(client):
    res = client.post(
        "/api/documents",
        json={
            "original_filename": "big.pdf",
            "size_bytes": 100 * 1024 * 1024 + 1,
        },
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "FILE_TOO_LARGE"
    assert res.get_json()["error"]["message"] == ERROR_MESSAGES["FILE_TOO_LARGE"]


def test_not_found_run(client):
    res = client.get(
        "/api/runs/00000000-0000-4000-8000-000000000099",
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 404
    assert res.get_json()["error"]["code"] == "NOT_FOUND"


def test_validation_missing_document_id(client):
    res = client.post("/api/runs", json={}, headers={"X-User-Id": "u1"})
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "VALIDATION_ERROR"
