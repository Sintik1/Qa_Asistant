"""Domain entities (not ORM / not HTTP DTOs)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    id: str
    user_id: str
    original_filename: str
    mime_type: str | None
    size_bytes: int
    storage_path: str
    status: str
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "storage_path": self.storage_path,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class GenerationRun:
    id: str
    user_id: str
    document_id: str
    status: str
    chunk_size: int = 4000
    chunk_overlap: int = 200
    chunk_method: str = "header"
    error_message: str | None = None
    case_count: int = 0
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "status": self.status,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunk_method": self.chunk_method,
            "error_message": self.error_message,
            "case_count": self.case_count,
            "created_at": self.created_at,
        }


@dataclass
class CaseRow:
    """One CSV-aligned test case row."""

    id: str
    run_id: str
    user_id: str
    name: str
    status: str
    step: str
    expected_result: str
    sort_order: int = 0
    chunk_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "user_id": self.user_id,
            "name": self.name,
            "status": self.status,
            "step": self.step,
            "expected_result": self.expected_result,
            "sort_order": self.sort_order,
            "chunk_id": self.chunk_id,
        }


@dataclass
class UserSettings:
    user_id: str
    chunk_size: int = 4000
    chunk_overlap: int = 200
    chunk_method: str = "header"
    has_api_token: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunk_method": self.chunk_method,
            "has_api_token": self.has_api_token,
        }


@dataclass
class CreateDocumentCommand:
    user_id: str
    original_filename: str
    size_bytes: int
    mime_type: str | None = None
    storage_path: str | None = None


@dataclass
class CreateRunCommand:
    user_id: str
    document_id: str
    chunk_size: int = 4000
    chunk_overlap: int = 200
    chunk_method: str = "header"


@dataclass
class UpdateTestCaseCommand:
    name: str | None = None
    status: str | None = None
    step: str | None = None
    expected_result: str | None = None
    sort_order: int | None = None
    fields: dict[str, Any] = field(default_factory=dict)
