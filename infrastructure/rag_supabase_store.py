"""Supabase PostgREST + RPC repositories for RAG chunks."""

from __future__ import annotations

from typing import Any, Sequence

from core.rag_models import (
    CaseChunkRecord,
    DocumentChunkRecord,
    IndexCaseChunkCommand,
    IndexDocumentChunkCommand,
)
from infrastructure.supabase_rest import SupabaseRestClient
from integrations.embedding_client import embedding_to_pgvector_literal


class SupabaseDocumentChunkRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def replace_for_document(
        self,
        document_id: str,
        user_id: str,
        chunks: Sequence[IndexDocumentChunkCommand],
    ) -> int:
        self._client.delete(
            "document_chunks",
            params={"document_id": f"eq.{document_id}", "user_id": f"eq.{user_id}"},
        )
        if not chunks:
            return 0
        rows = [
            {
                "user_id": c.user_id,
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
                "section_number": c.section_number,
                "section_path": c.section_path,
                "title": c.title,
                "content": c.content,
                "metadata": c.metadata,
                "embedding": embedding_to_pgvector_literal(c.embedding),
            }
            for c in chunks
        ]
        # Insert in batches to avoid huge payloads
        batch = 50
        total = 0
        for i in range(0, len(rows), batch):
            self._client.insert("document_chunks", rows[i : i + batch])
            total += len(rows[i : i + batch])
        return total

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        exclude_document_id: str | None = None,
        only_document_id: str | None = None,
    ) -> list[DocumentChunkRecord]:
        payload: dict[str, Any] = {
            "query_embedding": embedding_to_pgvector_literal(query_embedding),
            "match_count": match_count,
            "filter_user_id": user_id,
            "exclude_document_id": exclude_document_id,
            "only_document_id": only_document_id,
        }
        rows = self._client.rpc("match_document_chunks", payload)
        out: list[DocumentChunkRecord] = []
        for idx, row in enumerate(rows):
            out.append(
                DocumentChunkRecord(
                    id=str(row.get("id") or idx),
                    user_id=user_id,
                    document_id=str(row["document_id"]),
                    chunk_index=idx,
                    content=str(row.get("content") or ""),
                    section_number=row.get("section_number"),
                    section_path=row.get("section_path"),
                    title=row.get("title"),
                    metadata=row.get("metadata") or {},
                    similarity=float(row["similarity"])
                    if row.get("similarity") is not None
                    else None,
                )
            )
        return out


class SupabaseCaseChunkRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def upsert_many(self, chunks: Sequence[IndexCaseChunkCommand]) -> int:
        if not chunks:
            return 0
        rows = [
            {
                "user_id": c.user_id,
                "source_type": c.source_type,
                "test_case_id": c.test_case_id,
                "name": c.name,
                "status": c.status,
                "step": c.step,
                "expected_result": c.expected_result,
                "tags": list(c.tags),
                "content": c.content,
                "metadata": c.metadata,
                "embedding": embedding_to_pgvector_literal(c.embedding),
            }
            for c in chunks
        ]
        self._client.insert("case_chunks", rows)
        return len(rows)

    def match(
        self,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        match_count: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[CaseChunkRecord]:
        payload: dict[str, Any] = {
            "query_embedding": embedding_to_pgvector_literal(query_embedding),
            "match_count": match_count,
            "filter_user_id": user_id,
            "source_types": list(source_types or ["template", "approved_case"]),
        }
        rows = self._client.rpc("match_case_chunks", payload)
        out: list[CaseChunkRecord] = []
        for row in rows:
            tags = row.get("tags") or []
            out.append(
                CaseChunkRecord(
                    id=str(row.get("id")),
                    user_id=user_id,
                    source_type=str(row.get("source_type") or "template"),
                    name=str(row.get("name") or ""),
                    content=str(row.get("content") or ""),
                    status=str(row.get("status") or "Approved"),
                    step=str(row.get("step") or ""),
                    expected_result=str(row.get("expected_result") or ""),
                    tags=tuple(str(t) for t in tags),
                    similarity=float(row["similarity"])
                    if row.get("similarity") is not None
                    else None,
                )
            )
        return out
