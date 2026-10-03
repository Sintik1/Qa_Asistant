"""API: multipart upload + extract + storage sidecar."""

from __future__ import annotations

import io

import pytest
from docx import Document

from app import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path / "uploads"))
    application = create_app(testing=True)
    return application.test_client(), application


def test_upload_markdown(client):
    c, _ = client
    data = {
        "file": (io.BytesIO(b"# Auth\n\nUser logs in with password."), "reqs.md"),
    }
    res = c.post(
        "/api/documents/upload",
        data=data,
        content_type="multipart/form-data",
        headers={"X-User-Id": "u-upload-1"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["document"]["status"] == "extracted"
    assert body["document"]["storage_path"].startswith("documents/")
    assert "logs in" in body["text"]
    assert body["char_count"] == len(body["text"])


def test_upload_docx(client):
    c, _ = client
    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph("Checkout requires a valid cart with at least one item.")
    doc.save(buf)
    buf.seek(0)
    res = c.post(
        "/api/documents/upload",
        data={"file": (buf, "cart.docx")},
        content_type="multipart/form-data",
        headers={"X-User-Id": "u-upload-2"},
    )
    assert res.status_code == 201
    assert "valid cart" in res.get_json()["text"]


def test_upload_invalid_format(client):
    c, _ = client
    res = c.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(b"MZ"), "x.exe")},
        content_type="multipart/form-data",
        headers={"X-User-Id": "u-upload-3"},
    )
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "INVALID_FORMAT"


def test_generate_loads_extracted_text_from_storage(client):
    c, app = client

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            assert "password reset" in user_content
            return (
                "Name,Status,Step,Expected Result\n"
                "Reset,Approved,Open link,Password form opens\n"
            )

    app.extensions["ai_client"] = FakeAi()
    up = c.post(
        "/api/documents/upload",
        data={
            "file": (
                io.BytesIO(b"Feature: password reset via email token flow."),
                "reset.md",
            )
        },
        content_type="multipart/form-data",
        headers={"X-User-Id": "u-upload-4"},
    )
    doc_id = up.get_json()["document"]["id"]
    run = c.post(
        "/api/runs",
        json={"document_id": doc_id},
        headers={"X-User-Id": "u-upload-4"},
    ).get_json()
    gen = c.post(
        f"/api/runs/{run['id']}/generate",
        json={},  # no requirements_text — load from storage
        headers={"X-User-Id": "u-upload-4"},
    )
    assert gen.status_code == 200
    assert len(gen.get_json()["items"]) == 1
