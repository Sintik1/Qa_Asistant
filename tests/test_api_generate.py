"""POST /api/runs/<id>/generate — thin AI pipeline."""

from __future__ import annotations

import pytest

from app import create_app
from core.errors import AppError


class FakeAi:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.calls = 0

    def generate(self, system_prompt: str, user_content: str) -> str:
        self.calls += 1
        assert "CSV" in system_prompt or "тест" in system_prompt.lower()
        assert "Требования" in user_content
        return self.reply


class FailingAi:
    def generate(self, system_prompt: str, user_content: str) -> str:
        raise AppError(code="API_UNAVAILABLE", status_code=502)


@pytest.fixture()
def app_client():
    application = create_app(testing=True)
    return application, application.test_client()


def _seed_run(client, headers: dict) -> str:
    doc = client.post(
        "/api/documents",
        json={"original_filename": "reqs.md", "size_bytes": 64},
        headers=headers,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"], "chunk_size": 2000, "chunk_method": "header"},
        headers=headers,
    ).get_json()
    return run["id"]


def test_generate_persists_cases(app_client):
    app, client = app_client
    headers = {"X-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}
    run_id = _seed_run(client, headers)

    app.extensions["ai_client"] = FakeAi(
        "Name,Status,Step,Expected Result\n"
        "Login,Approved,Open login,Form visible\n"
        "Submit,Approved,Click OK,Success\n"
    )

    res = client.post(
        f"/api/runs/{run_id}/generate",
        json={
            "requirements_text": "User can log in with email and password.",
            "task_name": "Auth",
            "prompt": "positive cases",
        },
        headers=headers,
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["run"]["status"] == "completed"
    assert body["run"]["case_count"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["name"] == "Login"

    listed = client.get(f"/api/runs/{run_id}/test-cases", headers=headers)
    assert listed.status_code == 200
    assert len(listed.get_json()["items"]) == 2


def test_generate_missing_ai_token(app_client):
    app, client = app_client
    headers = {"X-User-Id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"}
    run_id = _seed_run(client, headers)
    app.extensions["ai_client"] = None

    res = client.post(
        f"/api/runs/{run_id}/generate",
        json={"requirements_text": "Enough text for requirements here."},
        headers=headers,
    )
    assert res.status_code == 503
    assert res.get_json()["error"]["code"] == "MISSING_TOKEN"


def test_generate_ai_unavailable(app_client):
    app, client = app_client
    headers = {"X-User-Id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"}
    run_id = _seed_run(client, headers)
    app.extensions["ai_client"] = FailingAi()

    res = client.post(
        f"/api/runs/{run_id}/generate",
        json={"requirements_text": "Enough text for requirements here."},
        headers=headers,
    )
    assert res.status_code == 502
    assert res.get_json()["error"]["code"] == "API_UNAVAILABLE"
