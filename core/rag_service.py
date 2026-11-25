"""RAG use-cases: index leaf sections, retrieve style/multi-doc context, chat."""

from __future__ import annotations

from typing import Protocol

from core.prompt_builder import append_selected_template, build_leaf_user_prompt
from core.rag_lexical import lexical_overlap
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


# Next page stays when its score is still in the same band as the previous one.
# This is the embedding gap, not a list of page names.
_SIMILARITY_CLUSTER_GAP = 0.02

# Confluence page-tree chrome, not the page body.
_PAGE_CHROME = ("назад к списку страниц",)


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
        return self._docs is not None and self._cases is not None and self._embedder is not None

    def index_document_text(
        self,
        *,
        user_id: str,
        document_id: str,
        text: str,
        extra_metadata: dict | None = None,
        as_single_chunk: bool = False,
    ) -> int:
        if self._docs is None or self._embedder is None:
            return 0
        if as_single_chunk:
            body = (text or "").strip()
            if not body:
                return self._docs.replace_for_document(document_id, user_id, [])
            return self._docs.replace_for_document(
                document_id,
                user_id,
                [
                    IndexDocumentChunkCommand(
                        user_id=user_id,
                        document_id=document_id,
                        chunk_index=0,
                        content=body,
                        embedding=self._embedder.embed(body[:8000]),
                        title=body.split("\n", 1)[0].lstrip("# ").strip() or None,
                        metadata={"source_shape": "page", **(extra_metadata or {})},
                    )
                ],
            )
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
                            "has_table": "|" in content or "TABLE_" in content,
                            **(extra_metadata or {}),
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
                    metadata={"flat": True, **(extra_metadata or {})},
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

    def retrieve_style_examples(self, *, user_id: str, query_text: str) -> list[CaseChunkRecord]:
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
        selected_template: str | None = None,
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
            template_examples=append_selected_template(template_block or None, selected_template),
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
        include_cases: bool = True,
        ai_generate,
    ) -> dict:
        if self._docs is None or self._embedder is None:
            return {
                "answer": "RAG не настроен: нет индекса чанков или embedder.",
                "citations": [],
            }
        emb = self._embedder.embed(question)
        semantic = bool(getattr(self._embedder, "semantic", False))
        # A semantic model ranks pages itself. Hash vectors do not, so the
        # offline path still keeps fragments that share words with the question.
        pool = self._chat_top_k if semantic else max(self._chat_top_k * 4, 200)
        hits = self._docs.match(
            user_id=user_id,
            query_embedding=emb,
            match_count=pool,
            only_document_id=document_id,
        )
        case_hits: list[CaseChunkRecord] = []
        if include_cases and self._cases is not None:
            case_hits = self._cases.match(
                user_id=user_id,
                query_embedding=emb,
                match_count=pool,
                source_types=["template", "approved_case"],
            )
        if not semantic:
            hits = _prefer_lexical(
                question,
                hits,
                lambda row: (row.title, row.section_path, row.content),
                self._chat_top_k,
            )
            docs_share_words = any(
                lexical_overlap(question, row.title, row.section_path, row.content) > 0
                for row in hits
            )
            case_hits = _prefer_lexical(
                question,
                case_hits,
                lambda row: (row.name, row.content, row.step),
                min(4, self._chat_top_k),
                fallback=not docs_share_words,
            )
        else:
            hits = hits[: self._chat_top_k]
            case_hits = case_hits[: min(4, self._chat_top_k)]
        if not hits and not case_hits:
            return {
                "answer": "По индексу требований ничего не найдено. Загрузите документ.",
                "citations": [],
            }
        if semantic:
            return _answer_from_similarity_cluster(hits, case_hits)
        quoted = _best_overlap(
            question,
            hits,
            lambda row: (row.title, row.section_path, row.content),
        )
        if not quoted:
            quoted = _best_overlap(
                question,
                case_hits,
                lambda row: (row.name, row.content, row.step),
            )
        citations = [_citation(row) for row in quoted]
        return {"answer": _verbatim(quoted), "citations": citations}


def _answer_from_similarity_cluster(hits: list, case_hits: list) -> dict:
    """Show every page that sits in the same similarity band. No page-name rules."""
    chosen = _similarity_cluster(list(hits) + list(case_hits))
    if not chosen:
        return {
            "answer": "По индексу требований ничего не найдено. Загрузите документ.",
            "citations": [],
        }
    answer = "\n\n".join(_page_markdown(row) for row in chosen if _page_markdown(row))
    return {
        "answer": answer,
        "citations": [_citation(row, preview="") for row in chosen],
    }


def _similarity_cluster(rows: list) -> list:
    ranked = sorted(rows, key=lambda row: float(getattr(row, "similarity", 0) or 0), reverse=True)
    if not ranked:
        return []
    chosen = [ranked[0]]
    for previous, row in zip(ranked, ranked[1:]):
        gap = float(getattr(previous, "similarity", 0) or 0) - float(getattr(row, "similarity", 0) or 0)
        if gap > _SIMILARITY_CLUSTER_GAP:
            break
        chosen.append(row)
    return chosen


def _page_markdown(row) -> str:
    return _without_page_chrome(getattr(row, "content", None) or "")


def _without_page_chrome(content: str) -> str:
    kept: list[str] = []
    for line in content.splitlines():
        normalized = line.strip().lower().rstrip(".")
        if normalized in _PAGE_CHROME:
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def _best_overlap(question: str, rows: list, text_of) -> list:
    """Keep only the fragments that share the most words with the question."""
    if not rows:
        return []
    scored = [
        (lexical_overlap(question, *text_of(row)), index, row)
        for index, row in enumerate(rows)
    ]
    top = max(item[0] for item in scored)
    if top > 0:
        return [item[2] for item in scored if item[0] == top]
    return [scored[0][2]]


def _verbatim(rows: list) -> str:
    parts: list[str] = []
    for row in rows:
        text = (getattr(row, "content", None) or "").strip()
        if text and text not in parts:
            parts.append(text)
    return "\n\n".join(parts)


def _citation(row, *, preview: str | None = None) -> dict:
    shown = (row.content or "")[:240] if preview is None else preview
    if hasattr(row, "document_id"):
        return {
            "document_id": row.document_id,
            "section_number": row.section_number,
            "section_path": row.section_path,
            "title": row.title,
            "similarity": row.similarity,
            "preview": shown,
            "source_kind": "requirement",
            "url": (row.metadata or {}).get("url") or None,
        }
    return {
        "document_id": row.test_case_id or row.id,
        "section_number": None,
        "section_path": row.name,
        "title": row.source_type,
        "similarity": row.similarity,
        "preview": shown,
        "source_kind": "case",
    }


def _prefer_lexical(
    question: str,
    rows: list,
    text_of,
    limit: int,
    *,
    fallback: bool = True,
) -> list:
    if not rows or limit <= 0:
        return []
    scored = [
        (
            lexical_overlap(question, *text_of(row)),
            float(row.similarity or 0.0),
            index,
            row,
        )
        for index, row in enumerate(rows)
    ]
    matched = [item for item in scored if item[0] > 0]
    if matched:
        pool = matched
    elif fallback:
        pool = scored
    else:
        return []
    pool.sort(key=lambda item: (item[0], item[1], -item[2]), reverse=True)
    return [item[3] for item in pool[:limit]]


def _format_style_block(rows: list[CaseChunkRecord]) -> str:
    if not rows:
        return ""
    parts = ["Примеры шаблонов / прошлых кейсов:"]
    for i, row in enumerate(rows, start=1):
        parts.append(f"{i}. [{row.source_type}] {row.name}\nStep: {row.step}\nExpected: {row.expected_result}")
    return "\n".join(parts)


def _format_related_block(rows: list[DocumentChunkRecord]) -> str:
    if not rows:
        return ""
    parts = ["Related requirements (другие документы пользователя):"]
    for i, row in enumerate(rows, start=1):
        parts.append(f"{i}. {row.section_path or row.title or row.document_id}\n{(row.content or '')[:1200]}")
    return "\n".join(parts)
