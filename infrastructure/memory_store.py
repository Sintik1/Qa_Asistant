"""In-memory repositories for local/pytest without live Supabase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from core.models import (
    CaseRow,
    CreateDocumentCommand,
    CreateRunCommand,
    Document,
    GenerationRun,
    UpdateTestCaseCommand,
    UserSettings,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryDocumentRepository:
    def __init__(self) -> None:
        self._items: dict[str, Document] = {}

    def create(self, cmd: CreateDocumentCommand) -> Document:
        doc_id = str(uuid.uuid4())
        path = cmd.storage_path or f"documents/{cmd.user_id}/{doc_id}/{cmd.original_filename}"
        doc = Document(
            id=doc_id,
            user_id=cmd.user_id,
            original_filename=cmd.original_filename,
            mime_type=cmd.mime_type,
            size_bytes=cmd.size_bytes,
            storage_path=path,
            status="uploaded",
            created_at=_now(),
        )
        self._items[doc_id] = doc
        return doc

    def get(self, document_id: str, user_id: str) -> Document | None:
        doc = self._items.get(document_id)
        if doc is None or doc.user_id != user_id:
            return None
        return doc

    def list_for_user(self, user_id: str) -> list[Document]:
        return sorted(
            [d for d in self._items.values() if d.user_id == user_id],
            key=lambda d: d.created_at or "",
            reverse=True,
        )

    def save(self, document: Document) -> Document:
        existing = self._items.get(document.id)
        if existing is None or existing.user_id != document.user_id:
            raise KeyError(document.id)
        self._items[document.id] = document
        return document


class MemoryRunRepository:
    def __init__(self) -> None:
        self._items: dict[str, GenerationRun] = {}

    def create(self, cmd: CreateRunCommand) -> GenerationRun:
        run_id = str(uuid.uuid4())
        run = GenerationRun(
            id=run_id,
            user_id=cmd.user_id,
            document_id=cmd.document_id,
            status="pending",
            chunk_size=cmd.chunk_size,
            chunk_overlap=cmd.chunk_overlap,
            chunk_method=cmd.chunk_method,
            created_at=_now(),
        )
        self._items[run_id] = run
        return run

    def get(self, run_id: str, user_id: str) -> GenerationRun | None:
        run = self._items.get(run_id)
        if run is None or run.user_id != user_id:
            return None
        return run

    def list_for_user(self, user_id: str) -> list[GenerationRun]:
        return sorted(
            [r for r in self._items.values() if r.user_id == user_id],
            key=lambda r: r.created_at or "",
            reverse=True,
        )

    def delete(self, run_id: str, user_id: str) -> bool:
        run = self.get(run_id, user_id)
        if run is None:
            return False
        del self._items[run_id]
        return True

    def save(self, run: GenerationRun) -> GenerationRun:
        self._items[run.id] = run
        return run


class MemoryTestCaseRepository:
    def __init__(self) -> None:
        self._items: dict[str, CaseRow] = {}

    def seed(self, case: CaseRow) -> CaseRow:
        self._items[case.id] = case
        return case

    def get(self, case_id: str, user_id: str) -> CaseRow | None:
        case = self._items.get(case_id)
        if case is None or case.user_id != user_id:
            return None
        return case

    def list_for_run(self, run_id: str, user_id: str) -> list[CaseRow]:
        rows = [c for c in self._items.values() if c.run_id == run_id and c.user_id == user_id]
        return sorted(rows, key=lambda c: c.sort_order)

    def replace_for_run(self, run_id: str, user_id: str, cases: list[CaseRow]) -> list[CaseRow]:
        to_delete = [cid for cid, c in self._items.items() if c.run_id == run_id and c.user_id == user_id]
        for cid in to_delete:
            del self._items[cid]
        for case in cases:
            self._items[case.id] = case
        return self.list_for_run(run_id, user_id)

    def update(self, case_id: str, user_id: str, cmd: UpdateTestCaseCommand) -> CaseRow | None:
        case = self._items.get(case_id)
        if case is None or case.user_id != user_id:
            return None
        if cmd.name is not None:
            case.name = cmd.name
        if cmd.status is not None:
            case.status = cmd.status
        if cmd.step is not None:
            case.step = cmd.step
        if cmd.expected_result is not None:
            case.expected_result = cmd.expected_result
        if cmd.sort_order is not None:
            case.sort_order = cmd.sort_order
        return case


class MemorySettingsRepository:
    def __init__(self) -> None:
        self._items: dict[str, UserSettings] = {}

    def get_or_create(self, user_id: str) -> UserSettings:
        if user_id not in self._items:
            self._items[user_id] = UserSettings(user_id=user_id)
        return self._items[user_id]

    def update(self, user_id: str, patch: dict) -> UserSettings:
        current = self.get_or_create(user_id)
        for key, value in patch.items():
            setattr(current, key, value)
        return current
