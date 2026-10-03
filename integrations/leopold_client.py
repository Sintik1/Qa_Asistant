"""Leopold API client — TZ production path via OpenAI-compatible HTTP."""

from __future__ import annotations

import os

from integrations.ai_client import (
    LEOPOLD_DEFAULT_MODEL,
    AiSettings,
    OpenAICompatibleClient,
    build_ai_client,
)

DEFAULT_MODEL = LEOPOLD_DEFAULT_MODEL


class LeopoldClient:
    """Leopold chat client (default model Qwen/Qwen2.5-72B-Instruct)."""

    def __init__(self, client: OpenAICompatibleClient) -> None:
        self._client = client

    @classmethod
    def from_env(cls) -> LeopoldClient | None:
        """Build Leopold client from URL+token regardless of AI_PROVIDER."""
        url = os.getenv("QA_ASISTANT_API_URL", "").strip()
        token = os.getenv("QA_ASISTANT_API_TOKEN", "").strip()
        if not url or not token:
            return None
        model = (
            os.getenv("QA_ASISTANT_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
        )
        client = build_ai_client(
            AiSettings(
                provider="leopold",
                api_url=url,
                api_token=token,
                model=model,
            )
        )
        if client is None:
            return None
        return cls(client)

    def generate(self, system_prompt: str, user_content: str) -> str:
        return self._client.generate(system_prompt, user_content)
