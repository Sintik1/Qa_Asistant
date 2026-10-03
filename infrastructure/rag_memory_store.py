"""In-memory RAG stores for pytest / offline."""

from __future__ import annotations

import math
import uuid
from typing import Sequence

from core.rag_models import (
    CaseChunkRecord,
    DocumentChunkRecord,
    IndexCaseChunkCommand,
    IndexDocumentChunkCommand,
)


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    dot = sum(float(a[i]) * float(b[i]) for i in range(n))
    na = math.sqrt(sum(float(a[i]) ** 2 for i in range(n))) or 1.0
    nb = math.sqrt(sum(float(b[i]) ** 2 for i in range(n))) or 1.0
    return dot / (na * nb)


class MemoryDocumentChunkRepository:
    def __init__(self) -> None:
        self._items: dict[str, tuple[IndexDocumentChunkCommand, str]] = {}

    def replace_for_document(
        self,
        document_id: str,
        user_id: str,
        chunks: Sequence[IndexDocumentChunkCommand],
    ) -> int:
        for key, (cmd, _) in list(self._items.items()):
            if cmd.document_id == document_id and cmd.user_id == user_id:
                del self._items[key]
        for cmd in chunks:
            self._items[str(uuid.uuid4())] = (cmd, cmd.user_id)
        return len(chunks)

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        exclude_document_id: str | None = None,
        only_document_id: str | None = None,
    ) -> list[DocumentChunkRecord]:
        scored: list[tuple[float, str, IndexDocumentChunkCommand]] = []
        for rid, (cmd, _) in self._items.items():
            if cmd.user_id != user_id:
                continue
            if exclude_document_id and cmd.document_id == exclude_document_id:
                continue
            if only_document_id and cmd.document_id != only_document_id:
                continue
            sim = _cosine(query_embedding, cmd.embedding)
            scored.append((sim, rid, cmd))
        scored.sort(key=lambda x: x[0], reverse=True)
        out: list[DocumentChunkRecord] = []
        for sim, rid, cmd in scored[: max(match_count, 1)]:
            out.append(
                DocumentChunkRecord(
                    id=rid,
                    user_id=cmd.user_id,
                    document_id=cmd.document_id,
                    chunk_index=cmd.chunk_index,
                    content=cmd.content,
                    section_number=cmd.section_number,
                    section_path=cmd.section_path,
                    title=cmd.title,
                    metadata=dict(cmd.metadata),
                    similarity=sim,
                )
            )
        return out


class MemoryCaseChunkRepository:
    def __init__(self) -> None:
        self._items: dict[str, IndexCaseChunkCommand] = {}

    def upsert_many(self, chunks: Sequence[IndexCaseChunkCommand]) -> int:
        for cmd in chunks:
            key = cmd.test_case_id or str(uuid.uuid4())
            self._items[key] = cmd
        return len(chunks)

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[CaseChunkRecord]:
        allowed = set(source_types or ["template", "approved_case"])
        scored: list[tuple[float, str, IndexCaseChunkCommand]] = []
        for rid, cmd in self._items.items():
            if cmd.user_id != user_id:
                continue
            if cmd.source_type not in allowed:
                continue
            sim = _cosine(query_embedding, cmd.embedding)
            scored.append((sim, rid, cmd))
        scored.sort(key=lambda x: x[0], reverse=True)
        out: list[CaseChunkRecord] = []
        for sim, rid, cmd in scored[: max(match_count, 1)]:
            out.append(
                CaseChunkRecord(
                    id=rid,
                    user_id=cmd.user_id,
                    source_type=cmd.source_type,
                    name=cmd.name,
                    content=cmd.content,
                    status=cmd.status,
                    step=cmd.step,
                    expected_result=cmd.expected_result,
                    tags=cmd.tags,
                    test_case_id=cmd.test_case_id,
                    metadata=dict(cmd.metadata),
                    similarity=sim,
                )
            )
        return out
