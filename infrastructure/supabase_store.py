"""Supabase PostgREST repositories — persist domain entities to Variant B tables."""

from __future__ import annotations

import uuid
from typing import Any

from core.models import (
    CaseRow,
    CreateDocumentCommand,
    CreateRunCommand,
    Document,
    GenerationRun,
    UpdateTestCaseCommand,
    UserSettings,
)
from infrastructure.supabase_rest import SupabaseRestClient

# Domain statuses ↔ Postgres enums (Variant B migration).
_DOC_TO_DB = {
    "uploaded": "uploaded",
    "extracted": "parsed",
    "parsed": "parsed",
    "failed": "failed",
}
_DOC_FROM_DB = {
    "uploaded": "uploaded",
    "parsed": "extracted",
    "failed": "failed",
}
_RUN_TO_DB = {
    "pending": "pending",
    "extracting": "extracting",
    "chunking": "chunking",
    "generating": "calling_ai",
    "calling_ai": "calling_ai",
    "validating": "validating",
    "completed": "done",
    "done": "done",
    "failed": "failed",
}
_RUN_FROM_DB = {
    "pending": "pending",
    "extracting": "extracting",
    "chunking": "chunking",
    "calling_ai": "generating",
    "validating": "validating",
    "done": "completed",
    "failed": "failed",
}


def _doc_from_row(row: dict[str, Any]) -> Document:
    return Document(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        original_filename=str(row["original_filename"]),
        mime_type=row.get("mime_type"),
        size_bytes=int(row.get("size_bytes") or 0),
        storage_path=str(row["storage_path"]),
        status=_DOC_FROM_DB.get(str(row.get("status") or "uploaded"), "uploaded"),
        created_at=str(row["created_at"]) if row.get("created_at") else None,
    )


def _run_from_row(row: dict[str, Any]) -> GenerationRun:
    return GenerationRun(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        document_id=str(row["document_id"]),
        status=_RUN_FROM_DB.get(str(row.get("status") or "pending"), "pending"),
        chunk_size=int(row.get("chunk_size") or 4000),
        chunk_overlap=int(row.get("chunk_overlap") or 200),
        chunk_method=str(row.get("chunk_method") or "header"),
        error_message=row.get("error_message"),
        case_count=int(row.get("case_count") or 0),
        created_at=str(row["created_at"]) if row.get("created_at") else None,
    )


def _case_from_row(row: dict[str, Any]) -> CaseRow:
    return CaseRow(
        id=str(row["id"]),
        run_id=str(row["run_id"]),
        user_id=str(row["user_id"]),
        name=str(row.get("name") or ""),
        status=str(row.get("status") or "Approved"),
        step=str(row.get("step") or ""),
        expected_result=str(row.get("expected_result") or ""),
        sort_order=int(row.get("sort_order") or 0),
        chunk_id=str(row["chunk_id"]) if row.get("chunk_id") else None,
    )


def _settings_from_row(row: dict[str, Any]) -> UserSettings:
    return UserSettings(
        user_id=str(row["user_id"]),
        chunk_size=int(row.get("chunk_size") or 4000),
        chunk_overlap=int(row.get("chunk_overlap") or 200),
        chunk_method=str(row.get("chunk_method") or "header"),
        has_api_token=bool(row.get("has_api_token")),
    )


class SupabaseDocumentRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def create(self, cmd: CreateDocumentCommand) -> Document:
        doc_id = str(uuid.uuid4())
        path = cmd.storage_path or f"documents/{cmd.user_id}/{doc_id}/{cmd.original_filename}"
        rows = self._client.insert(
            "documents",
            {
                "id": doc_id,
                "user_id": cmd.user_id,
                "original_filename": cmd.original_filename,
                "mime_type": cmd.mime_type,
                "size_bytes": cmd.size_bytes,
                "storage_path": path,
                "status": "uploaded",
            },
        )
        return _doc_from_row(rows[0])

    def get(self, document_id: str, user_id: str) -> Document | None:
        rows = self._client.select(
            "documents",
            params={"id": f"eq.{document_id}", "user_id": f"eq.{user_id}", "limit": "1"},
        )
        return _doc_from_row(rows[0]) if rows else None

    def list_for_user(self, user_id: str) -> list[Document]:
        rows = self._client.select(
            "documents",
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
            },
        )
        return [_doc_from_row(r) for r in rows]

    def save(self, document: Document) -> Document:
        rows = self._client.patch(
            "documents",
            params={"id": f"eq.{document.id}", "user_id": f"eq.{document.user_id}"},
            patch={
                "original_filename": document.original_filename,
                "mime_type": document.mime_type,
                "size_bytes": document.size_bytes,
                "storage_path": document.storage_path,
                "status": _DOC_TO_DB.get(document.status, "uploaded"),
            },
        )
        if not rows:
            raise KeyError(document.id)
        return _doc_from_row(rows[0])


class SupabaseRunRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def create(self, cmd: CreateRunCommand) -> GenerationRun:
        rows = self._client.insert(
            "generation_runs",
            {
                "user_id": cmd.user_id,
                "document_id": cmd.document_id,
                "status": "pending",
                "chunk_size": cmd.chunk_size,
                "chunk_overlap": cmd.chunk_overlap,
                "chunk_method": cmd.chunk_method,
            },
        )
        return _run_from_row(rows[0])

    def get(self, run_id: str, user_id: str) -> GenerationRun | None:
        rows = self._client.select(
            "generation_runs",
            params={"id": f"eq.{run_id}", "user_id": f"eq.{user_id}", "limit": "1"},
        )
        return _run_from_row(rows[0]) if rows else None

    def list_for_user(self, user_id: str) -> list[GenerationRun]:
        rows = self._client.select(
            "generation_runs",
            params={"user_id": f"eq.{user_id}", "order": "created_at.desc"},
        )
        return [_run_from_row(r) for r in rows]

    def delete(self, run_id: str, user_id: str) -> bool:
        existing = self.get(run_id, user_id)
        if existing is None:
            return False
        self._client.delete(
            "generation_runs",
            params={"id": f"eq.{run_id}", "user_id": f"eq.{user_id}"},
        )
        return True

    def save(self, run: GenerationRun) -> GenerationRun:
        rows = self._client.patch(
            "generation_runs",
            params={"id": f"eq.{run.id}", "user_id": f"eq.{run.user_id}"},
            patch={
                "status": _RUN_TO_DB.get(run.status, "pending"),
                "chunk_size": run.chunk_size,
                "chunk_overlap": run.chunk_overlap,
                "chunk_method": run.chunk_method,
                "error_message": run.error_message,
                "case_count": run.case_count,
            },
        )
        if not rows:
            raise KeyError(run.id)
        return _run_from_row(rows[0])


class SupabaseTestCaseRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def get(self, case_id: str, user_id: str) -> CaseRow | None:
        rows = self._client.select(
            "test_cases",
            params={"id": f"eq.{case_id}", "user_id": f"eq.{user_id}", "limit": "1"},
        )
        return _case_from_row(rows[0]) if rows else None

    def list_for_run(self, run_id: str, user_id: str) -> list[CaseRow]:
        rows = self._client.select(
            "test_cases",
            params={
                "run_id": f"eq.{run_id}",
                "user_id": f"eq.{user_id}",
                "order": "sort_order.asc",
            },
        )
        return [_case_from_row(r) for r in rows]

    def replace_for_run(self, run_id: str, user_id: str, cases: list[CaseRow]) -> list[CaseRow]:
        self._client.delete(
            "test_cases",
            params={"run_id": f"eq.{run_id}", "user_id": f"eq.{user_id}"},
        )
        if not cases:
            return []
        payload = [
            {
                "id": case.id,
                "run_id": run_id,
                "user_id": user_id,
                "name": case.name,
                "status": case.status or "Approved",
                "step": case.step if case.step.strip() else "-",
                "expected_result": case.expected_result or "",
                "sort_order": case.sort_order,
                "chunk_id": case.chunk_id,
            }
            for case in cases
        ]
        rows = self._client.insert("test_cases", payload)
        return [_case_from_row(r) for r in rows]

    def update(self, case_id: str, user_id: str, cmd: UpdateTestCaseCommand) -> CaseRow | None:
        patch: dict[str, Any] = {}
        if cmd.name is not None:
            patch["name"] = cmd.name
        if cmd.status is not None:
            patch["status"] = cmd.status
        if cmd.step is not None:
            patch["step"] = cmd.step if cmd.step.strip() else "-"
        if cmd.expected_result is not None:
            patch["expected_result"] = cmd.expected_result
        if cmd.sort_order is not None:
            patch["sort_order"] = cmd.sort_order
        if not patch:
            rows = self._client.select(
                "test_cases",
                params={"id": f"eq.{case_id}", "user_id": f"eq.{user_id}", "limit": "1"},
            )
            return _case_from_row(rows[0]) if rows else None
        rows = self._client.patch(
            "test_cases",
            params={"id": f"eq.{case_id}", "user_id": f"eq.{user_id}"},
            patch=patch,
        )
        return _case_from_row(rows[0]) if rows else None


class SupabaseSettingsRepository:
    def __init__(self, client: SupabaseRestClient) -> None:
        self._client = client

    def get_or_create(self, user_id: str) -> UserSettings:
        rows = self._client.select(
            "user_settings",
            params={"user_id": f"eq.{user_id}", "limit": "1"},
        )
        if rows:
            return _settings_from_row(rows[0])
        created = self._client.upsert(
            "user_settings",
            {
                "user_id": user_id,
                "chunk_size": 4000,
                "chunk_overlap": 200,
                "chunk_method": "header",
                "has_api_token": False,
            },
            on_conflict="user_id",
        )
        return _settings_from_row(created[0])

    def update(self, user_id: str, patch: dict) -> UserSettings:
        current = self.get_or_create(user_id)
        allowed = {"chunk_size", "chunk_overlap", "chunk_method", "has_api_token"}
        body = {
            "user_id": user_id,
            "chunk_size": current.chunk_size,
            "chunk_overlap": current.chunk_overlap,
            "chunk_method": current.chunk_method,
            "has_api_token": current.has_api_token,
        }
        for key, value in patch.items():
            if key in allowed:
                body[key] = value
        rows = self._client.upsert("user_settings", body, on_conflict="user_id")
        return _settings_from_row(rows[0])
