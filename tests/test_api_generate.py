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


def test_generate_passes_table_markers_to_model(app_client):
    app, client = app_client
    headers = {"X-User-Id": "dddddddd-dddd-4ddd-8ddd-dddddddddddd"}
    run_id = _seed_run(client, headers)
    seen: list[tuple[str, str]] = []

    class CapturingAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            seen.append((system_prompt, user_content))
            return (
                "Name,Status,Step,Expected Result\n"
                "Каталог,Approved,\"Проверить Email\",Поле string\n"
            )

    app.extensions["ai_client"] = CapturingAi()
    text = (
        "## 3. Каталог\n"
        "Поля карточки\n"
        "TABLE_BLOCK_BEGIN_1\n"
        "TABLE_1_START\n"
        "TABLE_1_COLUMNS: Поле || Тип\n"
        "TABLE_1_ROW_1: Email || string\n"
        "TABLE_BLOCK_END_1\n"
    )
    res = client.post(
        f"/api/runs/{run_id}/generate",
        json={"requirements_text": text},
        headers=headers,
    )
    assert res.status_code == 200, res.get_json()
    assert seen
    system_prompt, user_content = seen[0]
    assert "TABLE_N_START" in system_prompt
    assert "TABLE_1_ROW_1: Email || string" in user_content
    assert res.get_json()["items"][0]["name"] == "Каталог"


def test_generate_via_leopold_native_response(app_client):
    """Generate route parses CSV from Leopold's `response` field, not OpenAI choices."""
    from unittest.mock import MagicMock, patch

    from integrations.ai_client import AiSettings
    from integrations.leopold_native import LeopoldNativeClient

    app, client = app_client
    headers = {"X-User-Id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"}
    run_id = _seed_run(client, headers)
    app.extensions["ai_client"] = LeopoldNativeClient(
        AiSettings(
            provider="leopold",
            api_url="https://leopold.example/api/chat",
            api_token="secret-token",
            model="Qwen/Qwen2.5-72B-Instruct",
        )
    )
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": (
            "Name,Status,Step,Expected Result\n"
            "Login,Approved,Open page,Form is visible\n"
        )
    }
    with patch("integrations.leopold_native.httpx.Client") as client_cls:
        post = client_cls.return_value.__enter__.return_value.post
        post.return_value = mock_response
        res = client.post(
            f"/api/runs/{run_id}/generate",
            json={"requirements_text": "User can log in with email and password."},
            headers=headers,
        )
    assert res.status_code == 200, res.get_json()
    assert res.get_json()["items"][0]["name"] == "Login"
    payload = post.call_args.kwargs["json"]
    assert payload["chat"]["model"] == "Qwen/Qwen2.5-72B-Instruct"
    assert "User can log in" in payload["chat"]["contents"][0]["text"]
    assert "User can log in" in payload["chat"]["user_message"]
    assert "User can log in" in payload["chat"]["chat_history"][0]["content"]
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer secret-token"


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
