"""Unit tests for Ollama / Leopold AI factory (HTTP mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.errors import AppError
from integrations.ai_client import (
    AiSettings,
    OpenAICompatibleClient,
    build_ai_client,
    load_ai_settings,
)


def test_load_ai_settings_ollama_defaults(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.delenv("QA_ASISTANT_API_URL", raising=False)
    monkeypatch.delenv("QA_ASISTANT_MODEL", raising=False)
    monkeypatch.delenv("AI_OLLAMA_SIZE", raising=False)
    settings = load_ai_settings()
    assert settings.provider == "ollama"
    assert settings.model == "qwen2.5:1.5b"
    assert "11434" in settings.api_url
    assert build_ai_client(settings) is not None


def test_load_ai_settings_ollama_3b(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.delenv("QA_ASISTANT_MODEL", raising=False)
    monkeypatch.setenv("AI_OLLAMA_SIZE", "3b")
    assert load_ai_settings().model == "qwen2.5:3b"


def test_load_ai_settings_ollama_7b(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.delenv("QA_ASISTANT_MODEL", raising=False)
    monkeypatch.setenv("AI_OLLAMA_SIZE", "7b")
    assert load_ai_settings().model == "qwen2.5:7b"


def test_load_ai_settings_leopold_requires_creds(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "leopold")
    monkeypatch.delenv("QA_ASISTANT_API_URL", raising=False)
    monkeypatch.delenv("QA_ASISTANT_API_TOKEN", raising=False)
    monkeypatch.delenv("LEOPOLD_API_URL", raising=False)
    monkeypatch.delenv("LEOPOLD_TOKEN", raising=False)
    settings = load_ai_settings()
    assert settings.provider == "leopold"
    assert build_ai_client(settings) is None


def test_load_ai_settings_leopold_accepts_testsites_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "leopold")
    monkeypatch.delenv("QA_ASISTANT_API_URL", raising=False)
    monkeypatch.delenv("QA_ASISTANT_API_TOKEN", raising=False)
    monkeypatch.setenv("LEOPOLD_API_URL", "https://leopold.example/api/chat")
    monkeypatch.setenv("LEOPOLD_TOKEN", "secret-token")
    monkeypatch.delenv("QA_ASISTANT_MODEL", raising=False)
    settings = load_ai_settings()
    assert settings.api_url == "https://leopold.example/api/chat"
    assert settings.api_token == "secret-token"
    monkeypatch.setenv("QA_ASISTANT_API_URL", "http://localhost:11434/v1/chat/completions")
    monkeypatch.setenv("QA_ASISTANT_API_TOKEN", "ollama")
    settings = load_ai_settings()
    assert settings.api_url == "https://leopold.example/api/chat"
    assert settings.api_token == "secret-token"
    assert settings.model == "Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"
    client = build_ai_client(settings)
    assert client is not None
    assert client.__class__.__name__ == "LeopoldNativeClient"


def test_leopold_model_with_slash_overrides_qwen3(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "leopold")
    monkeypatch.setenv("LEOPOLD_API_URL", "https://leopold.example/api/1.0/lleopold/chatMulti")
    monkeypatch.setenv("LEOPOLD_TOKEN", "secret-token")
    monkeypatch.setenv("QA_ASISTANT_MODEL", "Qwen/Qwen2.5-72B-Instruct")
    assert load_ai_settings().model == "Qwen/Qwen2.5-72B-Instruct"


def test_leopold_payload_uses_qwen3_and_keeps_prompt_fields():
    from integrations.leopold_native import build_leopold_payload

    payload = build_leopold_payload("sys", "requirements", model="", temperature=0.0)
    chat = payload["chat"]
    assert chat["model"] == "Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"
    assert chat["system_prompt"] == "sys"
    assert chat["user_message"] == "requirements"
    assert chat["contents"][0]["text"] == "requirements"
    assert chat["chat_history"][0]["content"] == "requirements"
    assert chat["temperature"] == 0.0
    assert chat["max_new_tokens"] == 15000
    assert chat["contents"][0]["fileSize"] == 0


def test_leopold_native_reads_response_field():
    from integrations.leopold_native import LeopoldNativeClient

    settings = AiSettings(
        provider="leopold",
        api_url="https://leopold.example/api/chat",
        api_token="secret-token",
        model="Qwen/Qwen2.5-72B-Instruct",
    )
    client = LeopoldNativeClient(settings)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "Name,Status,Step,Expected Result\nLogin,Approved,Open page,Form is visible"
    }

    with patch("integrations.leopold_native.httpx.Client") as client_cls:
        post = client_cls.return_value.__enter__.return_value.post
        post.return_value = mock_response
        text = client.generate("sys", "requirements")

    assert text.startswith("Name,Status")
    payload = post.call_args.kwargs["json"]
    chat = payload["chat"]
    assert chat["system_prompt"] == "sys"
    assert chat["user_message"] == "requirements"
    assert chat["contents"][0]["text"] == "requirements"
    assert chat["contents"][0]["storageKey"] == ""
    assert chat["contents"][0]["fileSize"] == 0
    assert chat["contents"][0]["contentType"] == "text/plain"
    assert chat["chat_history"][0]["content"] == "requirements"
    assert chat["max_new_tokens"] == 15000
    assert chat["model"] == "Qwen/Qwen2.5-72B-Instruct"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer secret-token"


def test_openai_compatible_generate_ok():
    settings = AiSettings(
        provider="ollama",
        api_url="http://localhost:11434/v1/chat/completions",
        api_token="ollama",
        model="qwen2.5:7b",
    )
    client = OpenAICompatibleClient(settings)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "pong"}}]
    }

    with patch("integrations.ai_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        text = client.generate("sys", "ping")
    assert text == "pong"


def test_openai_compatible_maps_429():
    settings = AiSettings(
        provider="ollama",
        api_url="http://localhost:11434/v1/chat/completions",
        api_token="ollama",
        model="qwen2.5:7b",
    )
    client = OpenAICompatibleClient(settings)
    mock_response = MagicMock()
    mock_response.status_code = 429

    with patch("integrations.ai_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        with pytest.raises(AppError) as exc:
            client.generate("sys", "ping")
    assert exc.value.code == "API_429"


def test_put_ai_provider_switches_to_ollama(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "leopold")
    monkeypatch.setenv("LEOPOLD_API_URL", "https://leopold.example/api/chat")
    monkeypatch.setenv("LEOPOLD_TOKEN", "secret-token")
    monkeypatch.setenv("QA_ASISTANT_API_URL", "http://127.0.0.1:11434/v1/chat/completions")
    monkeypatch.setenv("QA_ASISTANT_API_TOKEN", "ollama")
    monkeypatch.setenv("QA_ASISTANT_MODEL", "qwen2.5:1.5b")
    from app import create_app

    app = create_app(testing=True)
    client = app.test_client()
    headers = {"X-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}
    before = client.get("/api/ai/provider", headers=headers)
    assert before.status_code == 200
    assert before.get_json()["provider"] == "leopold"
    assert before.get_json()["model"] == "Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"

    switched = client.put("/api/ai/provider", json={"provider": "ollama"}, headers=headers)
    assert switched.status_code == 200, switched.get_json()
    body = switched.get_json()
    assert body["provider"] == "ollama"
    assert body["model"] == "qwen2.5:1.5b"
    assert body["configured"] is True
    assert app.extensions["ai_client"].__class__.__name__ == "OpenAICompatibleClient"

    bad = client.put("/api/ai/provider", json={"provider": "other"}, headers=headers)
    assert bad.status_code == 422


def test_health_reports_ollama(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("QA_ASISTANT_MODEL", "qwen2.5:7b")
    from app import create_app

    app = create_app(testing=True)
    res = app.test_client().get("/api/health")
    assert res.status_code == 200
    ai = res.get_json()["ai"]
    assert ai["provider"] == "ollama"
    assert ai["model"] == "qwen2.5:7b"
    assert ai["configured"] is True


def test_ai_ping_uses_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    from app import create_app

    app = create_app(testing=True)
    fake = MagicMock()
    fake.generate.return_value = "pong"
    app.extensions["ai_client"] = fake
    res = app.test_client().post("/api/ai/ping", json={"prompt": "hi"})
    assert res.status_code == 200
    assert res.get_json()["reply"] == "pong"
    fake.generate.assert_called_once()
