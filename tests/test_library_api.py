"""Library CRUD stays per user and does not require AI."""

from __future__ import annotations

import io

import pytest

from app import create_app
from core.errors import ValidationError
from core.library_service import LibraryService
from infrastructure.library_store import MemoryLibraryRepository


@pytest.fixture()
def client():
    application = create_app(testing=True)
    return application.test_client()


def test_prompt_crud_and_user_isolation(client):
    owner = {"X-User-Id": "11111111-1111-4111-8111-111111111111"}
    other = {"X-User-Id": "22222222-2222-4222-8222-222222222222"}

    created = client.post(
        "/api/prompts",
        json={"name": "Негативные", "content": "Добавь негативные шаги"},
        headers=owner,
    )
    assert created.status_code == 201
    item_id = created.get_json()["id"]

    listed = client.get("/api/prompts", headers=owner)
    assert listed.status_code == 200
    assert [row["name"] for row in listed.get_json()["items"]] == ["Негативные"]

    hidden = client.get("/api/prompts", headers=other)
    assert hidden.get_json()["items"] == []

    renamed = client.patch(
        f"/api/prompts/{item_id}",
        json={"name": "Негативные v2"},
        headers=owner,
    )
    assert renamed.status_code == 200
    assert renamed.get_json()["name"] == "Негативные v2"

    missing = client.delete(f"/api/prompts/{item_id}", headers=other)
    assert missing.status_code == 404

    deleted = client.delete(f"/api/prompts/{item_id}", headers=owner)
    assert deleted.status_code == 204
    assert client.get("/api/prompts", headers=owner).get_json()["items"] == []


def test_template_duplicate_name_and_empty_text(client):
    headers = {"X-User-Id": "11111111-1111-4111-8111-111111111111"}
    first = client.post(
        "/api/scenario-templates",
        json={"name": "Тариф", "content": "Name CRM\nStep Проверить"},
        headers=headers,
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/scenario-templates",
        json={"name": "Тариф", "content": "другой текст шаблона"},
        headers=headers,
    )
    assert duplicate.status_code == 422
    assert "уже есть" in duplicate.get_json()["error"]["message"]

    empty = client.post(
        "/api/scenario-templates",
        json={"name": "  ", "content": "текст"},
        headers=headers,
    )
    assert empty.status_code == 422


def test_extract_requirements_longer_than_library_row(client):
    headers = {"X-User-Id": "11111111-1111-4111-8111-111111111111"}
    body = ("Требование к тарифу. " * 1200).encode()
    assert len(body) > 20_000
    extracted = client.post(
        "/api/library/extract-text",
        data={"file": (io.BytesIO(body), "requirements.md")},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert extracted.status_code == 200
    assert extracted.get_json()["char_count"] > 20_000


def test_extract_template_file_does_not_create_document(client):
    headers = {"X-User-Id": "11111111-1111-4111-8111-111111111111"}
    payload = io.BytesIO("Шаблон подключения тарифа для проверки.".encode())
    extracted = client.post(
        "/api/library/extract-text",
        data={"file": (payload, "template.md")},
        headers=headers,
        content_type="multipart/form-data",
    )
    assert extracted.status_code == 200
    assert "тарифа" in extracted.get_json()["text"]
    documents = client.get("/api/documents", headers=headers)
    assert documents.get_json()["items"] == []


def test_service_rejects_overlong_content():
    service = LibraryService(MemoryLibraryRepository(), kind_label="Промпт")
    with pytest.raises(ValidationError):
        service.create("user-1", "имя", "x" * 20_001)
