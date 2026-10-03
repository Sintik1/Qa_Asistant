"""API smoke: ≥3 CRUD operations on hybrid Flask API."""

from __future__ import annotations

import uuid

import pytest

from app import create_app
from core.models import CaseRow


@pytest.fixture()
def client():
    application = create_app(testing=True)
    return application.test_client(), application


def test_health(client):
    c, _ = client
    res = c.get("/api/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["mode"] == "hybrid-c"
    assert body["ai"]["provider"] in {"ollama", "leopold"}
    assert body["ai"]["model"]
    assert "configured" in body["ai"]


def test_crud_documents_runs_test_cases(client):
    c, app = client
    headers = {"X-User-Id": "11111111-1111-4111-8111-111111111111"}

    # Create document
    doc_res = c.post(
        "/api/documents",
        json={
            "original_filename": "reqs.md",
            "size_bytes": 128,
            "mime_type": "text/markdown",
        },
        headers=headers,
    )
    assert doc_res.status_code == 201
    doc = doc_res.get_json()
    assert doc["original_filename"] == "reqs.md"

    # Create run
    run_res = c.post(
        "/api/runs",
        json={"document_id": doc["id"], "chunk_method": "header"},
        headers=headers,
    )
    assert run_res.status_code == 201
    run = run_res.get_json()
    assert run["document_id"] == doc["id"]
    assert run["status"] == "pending"

    # Read runs
    list_res = c.get("/api/runs", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()["items"]) == 1

    # Seed + update test case (U)
    case_id = str(uuid.uuid4())
    with app.app_context():
        app.extensions["cases_repo"].seed(
            CaseRow(
                id=case_id,
                run_id=run["id"],
                user_id=headers["X-User-Id"],
                name="Login",
                status="Approved",
                step="Open app",
                expected_result="Home shown",
                sort_order=0,
            )
        )

    patch_res = c.patch(
        f"/api/test-cases/{case_id}",
        json={"step": "Open app\nClick login"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert "Click login" in patch_res.get_json()["step"]

    cases_res = c.get(f"/api/runs/{run['id']}/test-cases", headers=headers)
    assert cases_res.status_code == 200
    assert len(cases_res.get_json()["items"]) == 1

    # Delete run (D)
    del_res = c.delete(f"/api/runs/{run['id']}", headers=headers)
    assert del_res.status_code == 204
    assert c.get(f"/api/runs/{run['id']}", headers=headers).status_code == 404


def test_settings_patch(client):
    c, _ = client
    headers = {"X-User-Id": "22222222-2222-4222-8222-222222222222"}
    res = c.patch(
        "/api/settings",
        json={"chunk_size": 3000, "chunk_method": "fixed"},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["chunk_size"] == 3000
    assert body["chunk_method"] == "fixed"
