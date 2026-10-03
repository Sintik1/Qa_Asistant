"""Domain types for RAG indexing / retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentChunkRecord:
    id: str
    user_id: str
    document_id: str
    chunk_index: int
    content: str
    section_number: str | None = None
    section_path: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity: float | None = None


@dataclass(frozen=True)
class CaseChunkRecord:
    id: str
    user_id: str
    source_type: str
    name: str
    content: str
    status: str = "Approved"
    step: str = ""
    expected_result: str = ""
    tags: tuple[str, ...] = ()
    test_case_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity: float | None = None


@dataclass(frozen=True)
class IndexDocumentChunkCommand:
    user_id: str
    document_id: str
    chunk_index: int
    content: str
    embedding: list[float]
    section_number: str | None = None
    section_path: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IndexCaseChunkCommand:
    user_id: str
    source_type: str
    name: str
    content: str
    embedding: list[float]
    status: str = "Approved"
    step: str = ""
    expected_result: str = ""
    tags: tuple[str, ...] = ()
    test_case_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
