"""Embedding providers for RAG (Ollama / OpenAI-compatible / deterministic fallback)."""

from __future__ import annotations

import hashlib
import math
import os
import struct
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

import httpx

DEFAULT_DIMS = 768
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_DEFAULT_MODEL = "nomic-embed-text"


class EmbeddingClient(Protocol):
    @property
    def dims(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class EmbeddingSettings:
    provider: str
    api_url: str
    api_token: str
    model: str
    dims: int = DEFAULT_DIMS
    timeout_sec: float = 60.0

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.model)


def load_embedding_settings() -> EmbeddingSettings:
    provider = (os.getenv("EMBEDDING_PROVIDER") or "auto").strip().lower() or "auto"
    dims = int(os.getenv("EMBEDDING_DIMS") or str(DEFAULT_DIMS))
    timeout = float(os.getenv("EMBEDDING_TIMEOUT_SEC") or "60")
    token = (os.getenv("EMBEDDING_API_TOKEN") or os.getenv("QA_ASISTANT_API_TOKEN") or "").strip()
    model = (os.getenv("EMBEDDING_MODEL") or "").strip()
    url = (os.getenv("EMBEDDING_API_URL") or "").strip()

    if provider == "auto":
        # Prefer explicit embed URL; else Ollama if AI_PROVIDER=ollama; else hash fallback.
        ai_provider = (os.getenv("AI_PROVIDER") or "ollama").strip().lower()
        if url:
            provider = "openai_compat" if "/v1/" in url else "ollama"
        elif ai_provider == "ollama":
            provider = "ollama"
        else:
            provider = "hash"

    if provider == "ollama":
        return EmbeddingSettings(
            provider="ollama",
            api_url=url or OLLAMA_EMBED_URL,
            api_token=token or "ollama",
            model=model or OLLAMA_DEFAULT_MODEL,
            dims=dims,
            timeout_sec=timeout,
        )
    if provider in {"openai", "openai_compat", "leopold"}:
        return EmbeddingSettings(
            provider="openai_compat",
            api_url=url or "",
            api_token=token,
            model=model or "text-embedding-3-small",
            dims=dims,
            timeout_sec=timeout,
        )
    return EmbeddingSettings(
        provider="hash",
        api_url="",
        api_token="",
        model="hash-v1",
        dims=dims,
        timeout_sec=timeout,
    )


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _hash_embedding(text: str, dims: int) -> list[float]:
    """Deterministic local embedding for tests / offline (not semantic-quality)."""
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    out: list[float] = []
    block = seed
    while len(out) < dims:
        block = hashlib.sha256(block).digest()
        for i in range(0, len(block) - 3, 4):
            val = struct.unpack(">i", block[i : i + 4])[0] / 2147483647.0
            out.append(val)
            if len(out) >= dims:
                break
    return _l2_normalize(out[:dims])


@dataclass
class HashEmbeddingClient:
    dims: int = DEFAULT_DIMS

    def embed(self, text: str) -> list[float]:
        return _hash_embedding(text or "", self.dims)

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


@dataclass
class OllamaEmbeddingClient:
    settings: EmbeddingSettings

    @property
    def dims(self) -> int:
        return self.settings.dims

    def embed(self, text: str) -> list[float]:
        payload = {"model": self.settings.model, "prompt": text or " "}
        with httpx.Client(timeout=self.settings.timeout_sec) as client:
            response = client.post(self.settings.api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        vec = data.get("embedding") or []
        if not vec:
            raise RuntimeError("Empty embedding from Ollama")
        if len(vec) != self.settings.dims:
            # Pad / trim to configured dims so pgvector column stays consistent.
            if len(vec) < self.settings.dims:
                vec = list(vec) + [0.0] * (self.settings.dims - len(vec))
            else:
                vec = list(vec)[: self.settings.dims]
        return _l2_normalize([float(x) for x in vec])

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


@dataclass
class OpenAICompatEmbeddingClient:
    settings: EmbeddingSettings

    @property
    def dims(self) -> int:
        return self.settings.dims

    def embed(self, text: str) -> list[float]:
        headers = {"Content-Type": "application/json"}
        if self.settings.api_token:
            headers["Authorization"] = f"Bearer {self.settings.api_token}"
        payload = {"model": self.settings.model, "input": text or " "}
        with httpx.Client(timeout=self.settings.timeout_sec) as client:
            response = client.post(self.settings.api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        vec = data["data"][0]["embedding"]
        if len(vec) != self.settings.dims:
            if len(vec) < self.settings.dims:
                vec = list(vec) + [0.0] * (self.settings.dims - len(vec))
            else:
                vec = list(vec)[: self.settings.dims]
        return _l2_normalize([float(x) for x in vec])

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def build_embedding_client(
    settings: EmbeddingSettings | None = None,
) -> EmbeddingClient:
    cfg = settings or load_embedding_settings()
    if cfg.provider == "ollama" and cfg.api_url:
        return OllamaEmbeddingClient(cfg)
    if cfg.provider == "openai_compat" and cfg.api_url:
        return OpenAICompatEmbeddingClient(cfg)
    return HashEmbeddingClient(dims=cfg.dims)


def embedding_to_pgvector_literal(values: Sequence[float]) -> str:
    """PostgREST / pgvector text form: '[0.1,0.2,…]'."""
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"
