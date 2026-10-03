"""Application use-cases (orchestration)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Protocol

from core.case_parser import parse_cases_from_ai_text
from core.doc_reader import extract_text, validate_upload_meta
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
from core.prompt_builder import (
    FLAT_SYSTEM_PROMPT,
    SECTION_SYSTEM_PROMPT,
    iter_generation_prompts,
)
from core.rag_service import RagService
from core.repositories import DocumentRepository, RunRepository, SettingsRepository, TestCaseRepository
from core.section_parser import ParseOptions, ParsedDocument, parse_requirements_document


class AiGenerator(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str: ...


class DocumentBlobStore(Protocol):
    def save(
        self,
        *,
        user_id: str,
        document_id: str,
        filename: str,
        data: bytes,
        content_type: str | None,
        extracted_text: str,
    ) -> str: ...

    def read_extracted_text(self, storage_path: str) -> str | None: ...


# Backward-compatible alias for tests / callers that imported the flat prompt.
GENERATE_SYSTEM_PROMPT = FLAT_SYSTEM_PROMPT


def _validate_filename(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(code="INVALID_FORMAT")


class DocumentService:
    def __init__(
        self,
        docs: DocumentRepository,
        storage: DocumentBlobStore | None = None,
        rag_service: RagService | None = None,
    ) -> None:
        self._docs = docs
        self._storage = storage
        self._rag = rag_service

    def create(self, cmd: CreateDocumentCommand) -> Document:
        _validate_filename(cmd.original_filename)
        if cmd.size_bytes < 0:
            raise ValidationError(code="VALIDATION_ERROR", message="size_bytes must be >= 0")
        if cmd.size_bytes > MAX_FILE_SIZE_BYTES:
            raise ValidationError(code="FILE_TOO_LARGE")
        return self._docs.create(cmd)

    def upload_and_extract(
        self,
        *,
        user_id: str,
        filename: str,
        data: bytes,
        mime_type: str | None = None,
    ) -> tuple[Document, str, int]:
        """Validate → extract → persist blob/text → document meta (status=extracted)."""
        validate_upload_meta(filename, len(data))
        extracted = extract_text(filename, data)

        doc = self._docs.create(
            CreateDocumentCommand(
                user_id=user_id,
                original_filename=filename,
                size_bytes=len(data),
                mime_type=mime_type,
                storage_path=None,
            )
        )
        if self._storage is None:
            raise AppError(code="INTERNAL_ERROR", status_code=500)

        try:
            path = self._storage.save(
                user_id=user_id,
                document_id=doc.id,
                filename=filename,
                data=data,
                content_type=mime_type,
                extracted_text=extracted.text,
            )
        except Exception as exc:  # noqa: BLE001
            doc.status = "failed"
            self._docs.save(doc)
            raise AppError(code="INTERNAL_ERROR", status_code=500) from exc

        doc.storage_path = path
        doc.status = "extracted"
        self._docs.save(doc)
        if self._rag is not None:
            try:
                self._rag.index_document_text(
                    user_id=user_id,
                    document_id=doc.id,
                    text=extracted.text,
                )
            except Exception:
                # Indexing must not fail the upload/extract happy path.
                pass
        return doc, extracted.text, extracted.char_count

    def get(self, document_id: str, user_id: str) -> Document:
        doc = self._docs.get(document_id, user_id)
        if doc is None:
            raise NotFoundError()
        return doc

    def list_for_user(self, user_id: str) -> list[Document]:
        return self._docs.list_for_user(user_id)

    def load_extracted_text(self, document_id: str, user_id: str) -> str | None:
        doc = self.get(document_id, user_id)
        if self._storage is None:
            return None
        return self._storage.read_extracted_text(doc.storage_path)


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
    """Generate by leaf sections when outline exists; RAG enriches each leaf prompt."""

    def __init__(
        self,
        runs: RunRepository,
        docs: DocumentRepository,
        cases: TestCaseRepository,
        ai_client: AiGenerator | None,
        document_service: DocumentService | None = None,
        parse_options: ParseOptions | None = None,
        rag_service: RagService | None = None,
    ) -> None:
        self._runs = runs
        self._docs = docs
        self._cases = cases
        self._ai = ai_client
        self._document_service = document_service
        self._parse_options = parse_options or ParseOptions()
        self._rag = rag_service

    def parse_document(
        self, requirements_text: str, options: ParseOptions | None = None
    ) -> ParsedDocument:
        return parse_requirements_document(
            requirements_text, options=options or self._parse_options
        )

    def generate(
        self,
        run_id: str,
        user_id: str,
        *,
        requirements_text: str | None = None,
        task_name: str | None = None,
        prompt: str | None = None,
    ) -> tuple[GenerationRun, list[CaseRow]]:
        run = self._runs.get(run_id, user_id)
        if run is None:
            raise NotFoundError()
        if self._docs.get(run.document_id, user_id) is None:
            raise NotFoundError()

        text = (requirements_text or "").strip()
        if not text and self._document_service is not None:
            loaded = self._document_service.load_extracted_text(run.document_id, user_id)
            text = (loaded or "").strip()
        if not text:
            raise ValidationError(code="EMPTY_FILE")
        if len(text) < 8:
            raise ValidationError(code="NO_REQUIREMENTS")

        if self._ai is None:
            raise AppError(code="MISSING_TOKEN", status_code=503)

        run.status = "generating"
        run.error_message = None
        self._runs.save(run)

        # Ensure RAG index exists even if upload skipped indexing (text-only generate).
        if self._rag is not None:
            try:
                self._rag.index_document_text(
                    user_id=user_id,
                    document_id=run.document_id,
                    text=text,
                )
            except Exception:
                pass

        parsed_doc = self.parse_document(text)
        prompts: list[tuple[str, str, str | None]]
        if parsed_doc.leaves and self._rag is not None and self._rag.enabled:
            prompts = []
            for leaf in parsed_doc.leaves:
                user_prompt = self._rag.enrich_leaf_prompt(
                    leaf,
                    user_id=user_id,
                    document_id=run.document_id,
                    task_name=task_name,
                    extra_prompt=prompt,
                )
                prompts.append((SECTION_SYSTEM_PROMPT, user_prompt, leaf.number))
        else:
            prompts = iter_generation_prompts(
                parsed_doc,
                task_name=task_name,
                extra_prompt=prompt,
                raw_text_fallback=text,
            )

        all_parsed: list = []
        try:
            for system_prompt, user_prompt, _leaf_number in prompts:
                user_with_meta = (
                    f"{user_prompt}\n\n"
                    f"Параметры чанков: size={run.chunk_size}, "
                    f"overlap={run.chunk_overlap}, method={run.chunk_method}"
                )
                ai_text = self._ai.generate(system_prompt, user_with_meta)
                chunk_cases = parse_cases_from_ai_text(ai_text)
                all_parsed.extend(chunk_cases)
        except AppError as exc:
            run.status = "failed"
            run.error_message = exc.code
            self._runs.save(run)
            raise

        if not all_parsed:
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
            for idx, item in enumerate(all_parsed)
        ]
        saved = self._cases.replace_for_run(run.id, user_id, case_rows)
        if self._rag is not None:
            try:
                self._rag.index_approved_cases(
                    user_id=user_id,
                    cases=[c.to_dict() for c in saved],
                )
            except Exception:
                pass
        run.status = "completed"
        run.case_count = len(saved)
        run.error_message = None
        self._runs.save(run)
        return run, saved
