"""RAG repository protocols."""

from __future__ import annotations

from typing import Protocol, Sequence

from core.rag_models import (
    CaseChunkRecord,
    DocumentChunkRecord,
    IndexCaseChunkCommand,
    IndexDocumentChunkCommand,
)


class DocumentChunkRepository(Protocol):
    def replace_for_document(
        self, document_id: str, user_id: str, chunks: Sequence[IndexDocumentChunkCommand]
    ) -> int: ...

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        exclude_document_id: str | None = None,
        only_document_id: str | None = None,
    ) -> list[DocumentChunkRecord]: ...


class CaseChunkRepository(Protocol):
    def upsert_many(self, chunks: Sequence[IndexCaseChunkCommand]) -> int: ...

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[CaseChunkRecord]: ...
