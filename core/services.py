"""Application use-cases (orchestration)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Protocol

from core.case_parser import parse_cases_from_ai_text
from core.errors import AppError, NotFoundError, ValidationError
from core.messages import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
from core.models import (
    CreateDocumentCommand,
    CreateRunCommand,
    Document,
    GenerationRun,
    CaseRow,
    UpdateTestCaseCommand,
    UserSettings,
)
from core.repositories import DocumentRepository, RunRepository, SettingsRepository, TestCaseRepository


class AiGenerator(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str: ...


GENERATE_SYSTEM_PROMPT = (
    "Ты QA-инженер. По требованиям сгенерируй тест-кейсы. "
    "Ответь ТОЛЬКО CSV без пояснений, с заголовком:\n"
    "Name,Status,Step,Expected Result\n"
    "Status всегда Approved. Step может содержать несколько строк в кавычках CSV."
)


def _validate_filename(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(code="INVALID_FORMAT")


class DocumentService:
    def __init__(self, docs: DocumentRepository) -> None:
        self._docs = docs

    def create(self, cmd: CreateDocumentCommand) -> Document:
        _validate_filename(cmd.original_filename)
        if cmd.size_bytes < 0:
            raise ValidationError(code="VALIDATION_ERROR", message="size_bytes must be >= 0")
        if cmd.size_bytes > MAX_FILE_SIZE_BYTES:
            raise ValidationError(code="FILE_TOO_LARGE")
        return self._docs.create(cmd)

    def get(self, document_id: str, user_id: str) -> Document:
        doc = self._docs.get(document_id, user_id)
        if doc is None:
            raise NotFoundError()
        return doc

    def list_for_user(self, user_id: str) -> list[Document]:
        return self._docs.list_for_user(user_id)


class RunService:
    def __init__(self, runs: RunRepository, docs: DocumentRepository) -> None:
        self._runs = runs
        self._docs = docs

    def create(self, cmd: CreateRunCommand) -> GenerationRun:
        if self._docs.get(cmd.document_id, cmd.user_id) is None:
            raise NotFoundError()
        if cmd.chunk_size <= 0 or cmd.chunk_overlap < 0 or cmd.chunk_overlap >= cmd.chunk_size:
            raise ValidationError(code="VALIDATION_ERROR", message="Invalid chunk parameters")
        if cmd.chunk_method not in {"header", "fixed", "recursive"}:
            raise ValidationError(code="VALIDATION_ERROR", message="Invalid chunk_method")
        return self._runs.create(cmd)

    def get(self, run_id: str, user_id: str) -> GenerationRun:
        run = self._runs.get(run_id, user_id)
        if run is None:
            raise NotFoundError()
        return run

    def list_for_user(self, user_id: str) -> list[GenerationRun]:
        return self._runs.list_for_user(user_id)

    def delete(self, run_id: str, user_id: str) -> None:
        if not self._runs.delete(run_id, user_id):
            raise NotFoundError()


class TestCaseService:
    def __init__(self, cases: TestCaseRepository, runs: RunRepository) -> None:
        self._cases = cases
        self._runs = runs

    def list_for_run(self, run_id: str, user_id: str) -> list[CaseRow]:
        if self._runs.get(run_id, user_id) is None:
            raise NotFoundError()
        return self._cases.list_for_run(run_id, user_id)

    def update(self, case_id: str, user_id: str, cmd: UpdateTestCaseCommand) -> CaseRow:
        if cmd.step is not None and not cmd.step.strip():
            raise ValidationError(code="VALIDATION_ERROR", message="step must not be empty")
        updated = self._cases.update(case_id, user_id, cmd)
        if updated is None:
            raise NotFoundError()
        return updated


class SettingsService:
    def __init__(self, settings: SettingsRepository) -> None:
        self._settings = settings

    def get(self, user_id: str) -> UserSettings:
        return self._settings.get_or_create(user_id)

    def update(self, user_id: str, patch: dict) -> UserSettings:
        allowed = {"chunk_size", "chunk_overlap", "chunk_method", "has_api_token"}
        clean = {k: v for k, v in patch.items() if k in allowed}
        if not clean:
            raise ValidationError(code="VALIDATION_ERROR", message="No valid settings fields")
        if "chunk_size" in clean and int(clean["chunk_size"]) <= 0:
            raise ValidationError(code="VALIDATION_ERROR", message="Invalid chunk_size")
        if "chunk_method" in clean and clean["chunk_method"] not in {
            "header",
            "fixed",
            "recursive",
        }:
            raise ValidationError(code="VALIDATION_ERROR", message="Invalid chunk_method")
        return self._settings.update(user_id, clean)


class GenerationService:
    """Thin generate: AI text → parsed cases → persist on run."""

    def __init__(
        self,
        runs: RunRepository,
        docs: DocumentRepository,
        cases: TestCaseRepository,
        ai_client: AiGenerator | None,
    ) -> None:
        self._runs = runs
        self._docs = docs
        self._cases = cases
        self._ai = ai_client

    def generate(
        self,
        run_id: str,
        user_id: str,
        *,
        requirements_text: str,
        task_name: str | None = None,
        prompt: str | None = None,
    ) -> tuple[GenerationRun, list[CaseRow]]:
        run = self._runs.get(run_id, user_id)
        if run is None:
            raise NotFoundError()
        if self._docs.get(run.document_id, user_id) is None:
            raise NotFoundError()

        text = (requirements_text or "").strip()
        if not text:
            raise ValidationError(code="EMPTY_FILE")
        if len(text) < 8:
            raise ValidationError(code="NO_REQUIREMENTS")

        if self._ai is None:
            raise AppError(code="MISSING_TOKEN", status_code=503)

        run.status = "generating"
        run.error_message = None
        self._runs.save(run)

        user_parts = [f"Требования:\n{text}"]
        if task_name and task_name.strip():
            user_parts.append(f"Имя задачи: {task_name.strip()}")
        if prompt and prompt.strip():
            user_parts.append(f"Доп. промпт: {prompt.strip()}")
        user_parts.append(
            f"Параметры чанков: size={run.chunk_size}, "
            f"overlap={run.chunk_overlap}, method={run.chunk_method}"
        )

        try:
            ai_text = self._ai.generate(GENERATE_SYSTEM_PROMPT, "\n\n".join(user_parts))
        except AppError as exc:
            run.status = "failed"
            run.error_message = exc.code
            self._runs.save(run)
            raise

        parsed = parse_cases_from_ai_text(ai_text)
        if not parsed:
            run.status = "failed"
            run.error_message = "API_EMPTY"
            self._runs.save(run)
            raise AppError(code="API_EMPTY", status_code=502)

        case_rows = [
            CaseRow(
                id=str(uuid.uuid4()),
                run_id=run.id,
                user_id=user_id,
                name=item.name,
                status=item.status or "Approved",
                step=item.step,
                expected_result=item.expected_result,
                sort_order=idx,
            )
            for idx, item in enumerate(parsed)
        ]
        saved = self._cases.replace_for_run(run.id, user_id, case_rows)
        run.status = "completed"
        run.case_count = len(saved)
        run.error_message = None
        self._runs.save(run)
        return run, saved
