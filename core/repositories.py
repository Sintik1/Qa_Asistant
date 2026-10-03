"""Repository interfaces — implementations live in infrastructure/."""

from __future__ import annotations

from typing import Protocol

from core.models import (
    CreateDocumentCommand,
    CreateRunCommand,
    Document,
    GenerationRun,
    CaseRow,
    UpdateTestCaseCommand,
    UserSettings,
)


class DocumentRepository(Protocol):
    def create(self, cmd: CreateDocumentCommand) -> Document: ...
    def get(self, document_id: str, user_id: str) -> Document | None: ...
    def list_for_user(self, user_id: str) -> list[Document]: ...


class RunRepository(Protocol):
    def create(self, cmd: CreateRunCommand) -> GenerationRun: ...
    def get(self, run_id: str, user_id: str) -> GenerationRun | None: ...
    def list_for_user(self, user_id: str) -> list[GenerationRun]: ...
    def delete(self, run_id: str, user_id: str) -> bool: ...


class TestCaseRepository(Protocol):
    def list_for_run(self, run_id: str, user_id: str) -> list[CaseRow]: ...
    def update(
        self, case_id: str, user_id: str, cmd: UpdateTestCaseCommand
    ) -> CaseRow | None: ...


class SettingsRepository(Protocol):
    def get_or_create(self, user_id: str) -> UserSettings: ...
    def update(self, user_id: str, patch: dict) -> UserSettings: ...
