"""RAG use-cases: index leaf sections, retrieve style/multi-doc context, chat."""

from __future__ import annotations

from typing import Protocol

from core.prompt_builder import build_leaf_user_prompt
from core.rag_models import (
    CaseChunkRecord,
    DocumentChunkRecord,
    IndexCaseChunkCommand,
    IndexDocumentChunkCommand,
)
from core.rag_repository import CaseChunkRepository, DocumentChunkRepository
from core.section_parser import LeafSection, ParseOptions, parse_requirements_document


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


CHAT_SYSTEM_PROMPT = (
    "Ты помощник QA по требованиям. Отвечай только на основе переданных фрагментов. "
    "Если данных недостаточно — скажи об этом. В конце перечисли источники "
    "(section_path / document_id)."
)


class RagService:
    def __init__(
        self,
        *,
        doc_chunks: DocumentChunkRepository | None,
        case_chunks: CaseChunkRepository | None,
        embedder: Embedder | None,
        parse_options: ParseOptions | None = None,
        style_top_k: int = 4,
        multidoc_top_k: int = 4,
        chat_top_k: int = 6,
    ) -> None:
        self._docs = doc_chunks
        self._cases = case_chunks
        self._embedder = embedder
        self._parse_options = parse_options or ParseOptions()
        self._style_top_k = style_top_k
        self._multidoc_top_k = multidoc_top_k
        self._chat_top_k = chat_top_k

    @property
    def enabled(self) -> bool:
        return (
            self._docs is not None
            and self._cases is not None
            and self._embedder is not None
        )

    def index_document_text(
        self, *, user_id: str, document_id: str, text: str
    ) -> int:
        if self._docs is None or self._embedder is None:
            return 0
        parsed = parse_requirements_document(text, options=self._parse_options)
        commands: list[IndexDocumentChunkCommand] = []
        if parsed.leaves:
            for idx, leaf in enumerate(parsed.leaves):
                content = leaf.body or leaf.title
                emb = self._embedder.embed(f"{leaf.path}\n{content}")
                commands.append(
                    IndexDocumentChunkCommand(
                        user_id=user_id,
                        document_id=document_id,
                        chunk_index=idx,
                        content=content,
                        embedding=emb,
                        section_number=leaf.number,
                        section_path=leaf.path,
                        title=leaf.title,
                        metadata={
                            "item_count": len(leaf.items),
                            "has_table": "|" in content,
                        },
                    )
                )
        else:
            body = (text or "").strip()
            if not body:
                return self._docs.replace_for_document(document_id, user_id, [])
            emb = self._embedder.embed(body[:8000])
            commands.append(
                IndexDocumentChunkCommand(
                    user_id=user_id,
                    document_id=document_id,
                    chunk_index=0,
                    content=body,
                    embedding=emb,
                    section_number=None,
                    section_path="document",
                    title="document",
                    metadata={"flat": True},
                )
            )
        return self._docs.replace_for_document(document_id, user_id, commands)

    def index_case_commands(self, commands: list[IndexCaseChunkCommand]) -> int:
        if self._cases is None or not commands:
            return 0
        return self._cases.upsert_many(commands)

    def index_approved_cases(
        self,
        *,
        user_id: str,
        cases: list[dict],
    ) -> int:
        """Index generated/approved cases for style RAG (source_type=approved_case)."""
        if self._cases is None or self._embedder is None:
            return 0
        commands: list[IndexCaseChunkCommand] = []
        for case in cases:
            name = str(case.get("name") or "")
            step = str(case.get("step") or "")
            expected = str(case.get("expected_result") or "")
            status = str(case.get("status") or "Approved")
            content = f"{name}\n{step}\n{expected}".strip()
            if not content:
                continue
            emb = self._embedder.embed(content)
            commands.append(
                IndexCaseChunkCommand(
                    user_id=user_id,
                    source_type="approved_case",
                    name=name or "case",
                    content=content,
                    embedding=emb,
                    status=status,
                    step=step,
                    expected_result=expected,
                    tags=("approved",),
                    test_case_id=str(case["id"]) if case.get("id") else None,
                )
            )
        return self._cases.upsert_many(commands)

    def retrieve_style_examples(
        self, *, user_id: str, query_text: str
    ) -> list[CaseChunkRecord]:
        if self._cases is None or self._embedder is None:
            return []
        emb = self._embedder.embed(query_text)
        return self._cases.match(
            user_id=user_id,
            query_embedding=emb,
            match_count=self._style_top_k,
            source_types=["template", "approved_case"],
        )

    def retrieve_related_docs(
        self,
        *,
        user_id: str,
        query_text: str,
        exclude_document_id: str,
    ) -> list[DocumentChunkRecord]:
        if self._docs is None or self._embedder is None:
            return []
        emb = self._embedder.embed(query_text)
        return self._docs.match(
            user_id=user_id,
            query_embedding=emb,
            match_count=self._multidoc_top_k,
            exclude_document_id=exclude_document_id,
        )

    def enrich_leaf_prompt(
        self,
        leaf: LeafSection,
        *,
        user_id: str,
        document_id: str,
        task_name: str | None = None,
        extra_prompt: str | None = None,
    ) -> str:
        query = f"{leaf.path}\n{leaf.body}"[:4000]
        style = self.retrieve_style_examples(user_id=user_id, query_text=query)
        related = self.retrieve_related_docs(
            user_id=user_id,
            query_text=query,
            exclude_document_id=document_id,
        )
        template_block = _format_style_block(style)
        related_block = _format_related_block(related)
        base = build_leaf_user_prompt(
            leaf,
            task_name=task_name,
            extra_prompt=extra_prompt,
            template_examples=template_block or None,
        )
        if related_block:
            return f"{base}\n\n{related_block}"
        return base

    def chat(
        self,
        *,
        user_id: str,
        question: str,
        document_id: str | None = None,
        ai_generate,
    ) -> dict:
        if self._docs is None or self._embedder is None:
            return {
                "answer": "RAG не настроен: нет индекса чанков или embedder.",
                "citations": [],
            }
        emb = self._embedder.embed(question)
        hits = self._docs.match(
            user_id=user_id,
            query_embedding=emb,
            match_count=self._chat_top_k,
            only_document_id=document_id,
        )
        if not hits:
            return {
                "answer": "По индексу требований ничего не найдено. Загрузите документ.",
                "citations": [],
            }
        context = "\n\n".join(
            f"[{i + 1}] path={h.section_path or '-'} doc={h.document_id}\n{h.content[:2000]}"
            for i, h in enumerate(hits)
        )
        user_prompt = (
            f"Вопрос:\n{question.strip()}\n\nФрагменты требований:\n{context}"
        )
        answer = ai_generate(CHAT_SYSTEM_PROMPT, user_prompt)
        citations = [
            {
                "document_id": h.document_id,
                "section_number": h.section_number,
                "section_path": h.section_path,
                "title": h.title,
                "similarity": h.similarity,
                "preview": (h.content or "")[:240],
            }
            for h in hits
        ]
        return {"answer": answer, "citations": citations}


def _format_style_block(rows: list[CaseChunkRecord]) -> str:
    if not rows:
        return ""
    parts = ["Примеры шаблонов / прошлых кейсов:"]
    for i, row in enumerate(rows, start=1):
        parts.append(
            f"{i}. [{row.source_type}] {row.name}\n"
            f"Step: {row.step}\n"
            f"Expected: {row.expected_result}"
        )
    return "\n".join(parts)


def _format_related_block(rows: list[DocumentChunkRecord]) -> str:
    if not rows:
        return ""
    parts = ["Related requirements (другие документы пользователя):"]
    for i, row in enumerate(rows, start=1):
        parts.append(
            f"{i}. {row.section_path or row.title or row.document_id}\n"
            f"{(row.content or '')[:1200]}"
        )
    return "\n".join(parts)
