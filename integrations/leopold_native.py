"""Native Leopold chat client for ``/api/1.0/lleopold/chatMulti``.

OpenAI ``/v1/chat/completions`` is a different API. Leopold expects
``uuid`` + ``chat.system_prompt`` + ``chat.user_message`` + ``chat.contents``
and returns ``response``.
"""

from __future__ import annotations

import random
import time
from typing import Any

import httpx

from core.errors import AppError
from integrations.ai_client import LEOPOLD_DEFAULT_MODEL, AiSettings

LEOPOLD_MODEL = LEOPOLD_DEFAULT_MODEL


def _content_part(
    text: str,
    *,
    file_name: str,
    file_id: int,
    content_type: str,
    image_url: str = "",
    audio_url: str = "",
    audio_data: str = "",
    audio_format: str = "",
) -> dict[str, Any]:
    return {
        "type": "text",
        "text": text,
        "isUrl": True,
        "isAudioAsUrl": True,
        "storageKey": "",
        "fileSize": 0,
        "idFile": file_id,
        "fileName": file_name,
        "contentType": content_type,
        "image_url": {"url": image_url, "detail": "auto"},
        "audio_url": {"url": audio_url},
        "input_audio": {"data": audio_data, "format": audio_format},
    }


def build_leopold_payload(
    system_prompt: str,
    user_content: str,
    *,
    model: str,
    temperature: float | None = None,
) -> dict[str, Any]:
    text = user_content or ""
    return {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "chat": {
            "model": model or LEOPOLD_MODEL,
            "contents": [
                _content_part(
                    text,
                    file_name="prompt.txt",
                    file_id=12321,
                    content_type="text/plain",
                )
            ],
            "message_template": "<s>{role}\n{content}</s>",
            "response_template": "<s>bot\n",
            "system_prompt": system_prompt or "",
            "max_new_tokens": 15000,
            "no_repeat_ngram_size": 15,
            "repetition_penalty": 1.1,
            "temperature": 0.2 if temperature is None else temperature,
            "top_k": 40,
            "top_p": 0.9,
            "user_message": text,
            "chat_history": [
                {
                    "role": "user",
                    "content": text,
                    "contents": [
                        _content_part(
                            "string",
                            file_name="string",
                            file_id=1073741824,
                            content_type="",
                            image_url="string",
                            audio_url="string",
                            audio_data="string",
                            audio_format="string",
                        )
                    ],
                }
            ],
        },
    }


def extract_leopold_text(result: Any) -> str:
    """Pull assistant text from the shapes Leopold has returned in TestSites."""
    content = ""
    if isinstance(result, dict):
        if "response" in result:
            content = result.get("response", "")
            if isinstance(content, dict):
                content = content.get("text", "") or content.get("content", "") or ""
        elif "text" in result:
            content = result.get("text", "")
        elif "content" in result:
            content = result.get("content", "")
        elif "message" in result:
            message = result.get("message", {})
            if isinstance(message, dict):
                content = message.get("content", "") or message.get("text", "")
            elif isinstance(message, str):
                content = message
        elif "choices" in result:
            choices = result.get("choices") or []
            if choices and isinstance(choices[0], dict):
                first = choices[0]
                content = (
                    (first.get("message") or {}).get("content", "")
                    or first.get("text", "")
                    or first.get("content", "")
                )
        elif "data" in result:
            data = result.get("data", {})
            if isinstance(data, dict):
                content = data.get("response", "") or data.get("text", "") or data.get("content", "")
            elif isinstance(data, str):
                content = data
        if not content:
            for value in result.values():
                if isinstance(value, str) and value.strip():
                    content = value
                    break
                if isinstance(value, dict):
                    content = value.get("text", "") or value.get("content", "") or value.get("response", "")
                    if content:
                        break
    elif isinstance(result, list) and result:
        first = result[0]
        if isinstance(first, dict):
            content = first.get("response", "") or first.get("text", "") or first.get("content", "")
            if isinstance(content, dict):
                content = content.get("content", "") or content.get("text", "")
        elif isinstance(first, str):
            content = first
    elif isinstance(result, str):
        content = result
    return str(content or "").strip()


class LeopoldNativeClient:
    """HTTP client for Leopold's own chat contract."""

    def __init__(self, settings: AiSettings) -> None:
        self.settings = settings

    def generate(
        self,
        system_prompt: str,
        user_content: str,
        *,
        temperature: float | None = None,
    ) -> str:
        payload = build_leopold_payload(
            system_prompt,
            user_content,
            model=self.settings.model or LEOPOLD_MODEL,
            temperature=temperature,
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.api_token}",
        }
        timeout = httpx.Timeout(self.settings.timeout_sec, connect=30.0)
        response: httpx.Response | None = None
        max_attempts = 3
        try:
            with httpx.Client(timeout=timeout) as client:
                for attempt in range(1, max_attempts + 1):
                    try:
                        response = client.post(self.settings.api_url, headers=headers, json=payload)
                    except httpx.TimeoutException as exc:
                        if attempt < max_attempts:
                            time.sleep(min(2, attempt) + random.random() * 0.01)
                            continue
                        raise AppError(code="API_UNAVAILABLE", status_code=502) from exc
                    except httpx.HTTPError as exc:
                        raise AppError(code="API_UNAVAILABLE", status_code=502) from exc

                    if response.status_code in {502, 503, 504} and attempt < max_attempts:
                        time.sleep(min(2, attempt) + random.random() * 0.01)
                        continue
                    break
        except AppError:
            raise

        if response is None:
            raise AppError(code="API_UNAVAILABLE", status_code=502)
        if response.status_code == 401:
            raise AppError(code="INVALID_TOKEN", status_code=401)
        if response.status_code == 429:
            raise AppError(code="API_429", status_code=429)
        if response.status_code == 503:
            raise AppError(code="API_503", status_code=503)
        if response.status_code >= 400:
            raise AppError(code="API_UNAVAILABLE", status_code=502)

        try:
            data = response.json()
        except ValueError as exc:
            raise AppError(code="API_EMPTY", status_code=502) from exc
        text = extract_leopold_text(data)
        if not text:
            raise AppError(code="API_EMPTY", status_code=502)
        return text
