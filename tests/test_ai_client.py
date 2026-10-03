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
    settings = load_ai_settings()
    assert settings.provider == "leopold"
    assert build_ai_client(settings) is None


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
