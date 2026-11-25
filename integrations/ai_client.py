"""AI providers: Ollama (local Qwen) and Leopold (TZ). OpenAI-compatible chat API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from core.errors import AppError

LEOPOLD_DEFAULT_MODEL = "Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"
OLLAMA_DEFAULT_MODEL_1_5B = "qwen2.5:1.5b"
OLLAMA_DEFAULT_MODEL_3B = "qwen2.5:3b"
OLLAMA_DEFAULT_MODEL_7B = "qwen2.5:7b"
OLLAMA_DEFAULT_MODEL_14B = "qwen2.5:14b"
OLLAMA_DEFAULT_URL = "http://localhost:11434/v1/chat/completions"


class AiClient(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str: ...


@dataclass(frozen=True)
class AiSettings:
    provider: str
    api_url: str
    api_token: str
    model: str
    timeout_sec: float = 300.0

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.model)


@dataclass
class OpenAICompatibleClient:
    """Shared client for Leopold / Ollama (OpenAI chat.completions shape)."""

    settings: AiSettings

    def generate(
        self,
        system_prompt: str,
        user_content: str,
        *,
        temperature: float | None = None,
    ) -> str:
        headers = {"Content-Type": "application/json"}
        if self.settings.api_token:
            headers["Authorization"] = f"Bearer {self.settings.api_token}"

        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        try:
            with httpx.Client(timeout=self.settings.timeout_sec) as client:
                response = client.post(self.settings.api_url, headers=headers, json=payload)
        except httpx.ConnectError as exc:
            raise AppError(code="API_UNAVAILABLE", status_code=502) from exc
        except httpx.TimeoutException as exc:
            raise AppError(code="API_UNAVAILABLE", status_code=502) from exc
        except httpx.HTTPError as exc:
            raise AppError(code="API_UNAVAILABLE", status_code=502) from exc

        if response.status_code == 401:
            raise AppError(code="INVALID_TOKEN", status_code=401)
        if response.status_code == 429:
            raise AppError(code="API_429", status_code=429)
        if response.status_code == 503:
            raise AppError(code="API_503", status_code=503)
        if response.status_code >= 400:
            raise AppError(code="API_UNAVAILABLE", status_code=502)

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not str(content).strip():
            raise AppError(code="API_EMPTY", status_code=502)
        return str(content)


def _ollama_model_from_env() -> str:
    """Prefer explicit model; else map AI_OLLAMA_SIZE (default 1.5b for 8GB Macs)."""
    explicit = os.getenv("QA_ASISTANT_MODEL", "").strip()
    if explicit:
        return explicit
    size = os.getenv("AI_OLLAMA_SIZE", "1.5b").strip().lower()
    if size in {"14b", "14", "qwen2.5:14b"}:
        return OLLAMA_DEFAULT_MODEL_14B
    if size in {"7b", "7", "qwen2.5:7b"}:
        return OLLAMA_DEFAULT_MODEL_7B
    if size in {"3b", "3", "qwen2.5:3b"}:
        return OLLAMA_DEFAULT_MODEL_3B
    return OLLAMA_DEFAULT_MODEL_1_5B


def load_ai_settings() -> AiSettings:
    """
    AI_PROVIDER:
      - ollama  (default for local study/debug)
      - leopold (TZ / production path)
    """
    provider = os.getenv("AI_PROVIDER", "ollama").strip().lower() or "ollama"
    timeout = float(os.getenv("AI_TIMEOUT_SEC", "300"))

    if provider == "leopold":
        # LEOPOLD_* wins: QA_ASISTANT_* is also the Ollama URL/token in this repo.
        url = (
            os.getenv("LEOPOLD_API_URL", "").strip()
            or os.getenv("QA_ASISTANT_API_URL", "").strip()
        )
        token = (
            os.getenv("LEOPOLD_TOKEN", "").strip()
            or os.getenv("QA_ASISTANT_API_TOKEN", "").strip()
        )
        # QA_ASISTANT_MODEL is the Ollama tag in this repo (qwen2.5:1.5b).
        # Leopold needs a provider model id, not that tag.
        model_env = os.getenv("QA_ASISTANT_MODEL", "").strip()
        model = model_env if "/" in model_env else LEOPOLD_DEFAULT_MODEL
        return AiSettings(
            provider="leopold",
            api_url=url,
            api_token=token,
            model=model,
            timeout_sec=timeout,
        )

    # ollama (and any future openai_compat defaults)
    url = os.getenv("QA_ASISTANT_API_URL", "").strip() or OLLAMA_DEFAULT_URL
    token = os.getenv("QA_ASISTANT_API_TOKEN", "").strip() or "ollama"
    model = _ollama_model_from_env()
    return AiSettings(
        provider="ollama",
        api_url=url,
        api_token=token,
        model=model,
        timeout_sec=timeout,
    )


def activate_ai_provider(provider: str) -> tuple[AiSettings, AiClient | None]:
    """Switch the process to ollama or leopold and return the new client."""
    name = (provider or "").strip().lower()
    if name not in {"ollama", "leopold"}:
        raise ValueError(name)
    os.environ["AI_PROVIDER"] = name
    settings = load_ai_settings()
    return settings, build_ai_client(settings)


def persist_ai_provider(provider: str, env_path: str | None = None) -> None:
    """Remember the switch in `.env` so the next process start keeps it."""
    import re
    from pathlib import Path

    path = Path(env_path) if env_path else Path(__file__).resolve().parents[1] / ".env"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    line = f"AI_PROVIDER={provider}"
    if re.search(r"(?m)^AI_PROVIDER=", text):
        text = re.sub(r"(?m)^AI_PROVIDER=.*$", line, text, count=1)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    path.write_text(text, encoding="utf-8")


def build_ai_client(settings: AiSettings | None = None) -> AiClient | None:
    cfg = settings or load_ai_settings()
    if cfg.provider == "leopold":
        if not cfg.api_url or not cfg.api_token:
            return None
        from integrations.leopold_native import LeopoldNativeClient

        return LeopoldNativeClient(cfg)
    if not cfg.api_url or not cfg.model:
        return None
    return OpenAICompatibleClient(cfg)


def ai_status_dict() -> dict[str, Any]:
    settings = load_ai_settings()
    client = build_ai_client(settings)
    return {
        "provider": settings.provider,
        "model": settings.model,
        "api_url": settings.api_url,
        "configured": client is not None,
        "hint": (
            "8GB Mac: qwen2.5:1.5b (default). Optional: 3b. Avoid 7b/14b."
            if settings.provider == "ollama"
            else "Set LEOPOLD_API_URL + LEOPOLD_TOKEN (or QA_ASISTANT_API_URL + QA_ASISTANT_API_TOKEN)"
        ),
    }
