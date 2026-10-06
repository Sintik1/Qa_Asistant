"""Full business-logic coverage for DZ step 8 (upload → generate → CRUD → errors)."""

from __future__ import annotations

import io

import pytest

from app import create_app
from core.case_parser import parse_cases_from_ai_text
from core.doc_reader import extract_text
from core.messages import ERROR_MESSAGES


CSV_REPLY = (
    "Name,Status,Step,Expected Result\n"
    "Login OK,Approved,Open /login|Submit form,Dashboard opens\n"
    "Login fail,Approved,Open /login|Wrong password,Error shown\n"
)


class FakeAi:
    def __init__(self, reply: str = CSV_REPLY) -> None:
        self.reply = reply
        self.calls = 0

    def generate(self, system_prompt: str, user_content: str) -> str:
        self.calls += 1
        return self.reply


@pytest.fixture()
def app_client(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path / "uploads"))
    monkeypatch.delenv("AUTH_DEV_BYPASS", raising=False)
    application = create_app(testing=True)
    application.extensions["ai_client"] = FakeAi()
    return application, application.test_client()


@pytest.fixture()
def bypass_client(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("AUTH_DEV_BYPASS", "1")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "unit-test-secret")
    # Non-testing app still must not hit real PostgREST (proxy/network flakiness).
    monkeypatch.setenv("PERSIST_BACKEND", "memory")
    application = create_app(testing=False)
    application.extensions["ai_client"] = FakeAi()
    return application.test_client()


def test_happy_path_upload_generate_patch_delete(app_client):
    app, client = app_client
    headers = {"X-User-Id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"}

    up = client.post(
        "/api/documents/upload",
        data={
            "file": (
                io.BytesIO("# Auth\n\nUser logs in with email and password.\n".encode()),
                "auth.md",
            )
        },
        content_type="multipart/form-data",
        headers=headers,
    )
    assert up.status_code == 201
    body = up.get_json()
    assert body["char_count"] > 0
    doc_id = body["document"]["id"]
    text = body["text"]

    run = client.post(
        "/api/runs",
        json={"document_id": doc_id, "chunk_method": "header"},
        headers=headers,
    )
    assert run.status_code == 201
    run_id = run.get_json()["id"]

    gen = client.post(
        f"/api/runs/{run_id}/generate",
        json={
            "requirements_text": text,
            "task_name": "Auth",
            "prompt": "2 cases",
        },
        headers=headers,
    )
    assert gen.status_code == 200
    items = gen.get_json()["items"]
    assert len(items) == 2
    assert items[0]["name"] == "Login OK"
    assert app.extensions["ai_client"].calls == 1

    cases = client.get(f"/api/runs/{run_id}/test-cases", headers=headers)
    assert cases.status_code == 200
    assert len(cases.get_json()["items"]) == 2

    case_id = items[0]["id"]
    patched = client.patch(
        f"/api/test-cases/{case_id}",
        json={"step": "1. Open login\n2. Submit"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert "Open login" in patched.get_json()["step"]

    settings = client.patch(
        "/api/settings",
        json={"chunk_size": 3200},
        headers=headers,
    )
    assert settings.status_code == 200
    assert settings.get_json()["chunk_size"] == 3200

    deleted = client.delete(f"/api/runs/{run_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/runs/{run_id}", headers=headers).status_code == 404


def test_auth_dev_bypass_defaults_user_without_header(bypass_client):
    res = bypass_client.get("/api/runs")
    assert res.status_code == 200
    assert res.get_json()["items"] == []


def test_auth_dev_bypass_still_honors_x_skip_auth(bypass_client):
    res = bypass_client.get("/api/runs", headers={"X-Skip-Auth": "1"})
    assert res.status_code == 401
    err = res.get_json()["error"]
    assert err["code"] == "UNAUTHORIZED"
    assert err["message"] == ERROR_MESSAGES["UNAUTHORIZED"]
    assert err.get("request_id")


def test_invalid_upload_and_meta_validation(app_client):
    _, client = app_client
    headers = {"X-User-Id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"}

    bad_meta = client.post(
        "/api/documents",
        json={"original_filename": "virus.exe", "size_bytes": 10},
        headers=headers,
    )
    assert bad_meta.status_code == 422
    assert bad_meta.get_json()["error"]["code"] == "INVALID_FORMAT"
    assert (
        bad_meta.get_json()["error"]["message"] == ERROR_MESSAGES["INVALID_FORMAT"]
    )

    too_big = client.post(
        "/api/documents",
        json={"original_filename": "big.md", "size_bytes": 200 * 1024 * 1024},
        headers=headers,
    )
    assert too_big.status_code == 422
    assert too_big.get_json()["error"]["code"] == "FILE_TOO_LARGE"

    bad_upload = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(b"MZ"), "malware.exe")},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert bad_upload.status_code == 422
    assert bad_upload.get_json()["error"]["code"] == "INVALID_FORMAT"


def test_parse_engine_and_doc_reader_unit():
    cases = parse_cases_from_ai_text(CSV_REPLY)
    assert len(cases) == 2
    assert cases[0].name == "Login OK"
    assert "Open /login" in cases[0].step

    extracted = extract_text("note.md", b"# Title\n\nHello world\n")
    assert "Hello world" in extracted.text
    assert extracted.char_count == len(extracted.text)
