"""Unit tests for embeddings, section→index, retrieve helpers."""

from __future__ import annotations

from core.rag_models import IndexCaseChunkCommand, IndexDocumentChunkCommand
from core.rag_service import RagService
from core.section_parser import parse_requirements_document
from infrastructure.rag_memory_store import (
    MemoryCaseChunkRepository,
    MemoryDocumentChunkRepository,
)
from integrations.embedding_client import (
    HashEmbeddingClient,
    embedding_to_pgvector_literal,
    load_embedding_settings,
)


def test_hash_embedding_deterministic_and_normalized():
    client = HashEmbeddingClient(dims=768)
    a = client.embed("роутер рассрочка")
    b = client.embed("роутер рассрочка")
    c = client.embed("совсем другой текст")
    assert len(a) == 768
    assert a == b
    assert a != c
    # L2 ~ 1
    norm = sum(x * x for x in a) ** 0.5
    assert 0.99 <= norm <= 1.01


def test_pgvector_literal_format():
    lit = embedding_to_pgvector_literal([0.1, -0.2, 0.3])
    assert lit.startswith("[") and lit.endswith("]")
    assert "0.10000000" in lit


def test_load_embedding_settings_hash_in_testing(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "hash")
    cfg = load_embedding_settings()
    assert cfg.provider == "hash"
    assert cfg.dims == 768


def test_rag_index_and_multidoc_exclude_current():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb, multidoc_top_k=3)

    text_a = "## СИСТЕМА 1\nНастроить рассрочку на 24 месяца для роутера.\n"
    text_b = "## СИСТЕМА 2\nЗаказ нового оборудования по акции недоступен.\n"
    n1 = rag.index_document_text(user_id="u1", document_id="doc-a", text=text_a)
    n2 = rag.index_document_text(user_id="u1", document_id="doc-b", text=text_b)
    assert n1 >= 1 and n2 >= 1

    related = rag.retrieve_related_docs(
        user_id="u1",
        query_text="заказ по акции недоступен",
        exclude_document_id="doc-a",
    )
    assert related
    assert all(r.document_id != "doc-a" for r in related)
    assert any(r.document_id == "doc-b" for r in related)


def test_rag_style_retrieve_after_template_index():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb, style_top_k=2)

    vec = emb.embed("лимит рассрочки запрет")
    cases.upsert_many(
        [
            IndexCaseChunkCommand(
                user_id="u1",
                source_type="template",
                name="Негатив лимит",
                content="Негатив лимит\nПревысить лимит\nПокупка запрещена",
                embedding=vec,
                step="Превысить лимит",
                expected_result="Покупка запрещена",
                tags=("negative",),
            )
        ]
    )
    hits = rag.retrieve_style_examples(user_id="u1", query_text="лимит рассрочки")
    assert hits
    assert hits[0].name == "Негатив лимит"


def test_enrich_leaf_prompt_contains_style_and_related():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb)

    rag.index_document_text(
        user_id="u1",
        document_id="other",
        text="## СИСТЕМА 2\nЗаказ нового об-я по акции недоступно.\n",
    )
    cases.upsert_many(
        [
            IndexCaseChunkCommand(
                user_id="u1",
                source_type="template",
                name="Позитив заказ",
                content="Позитив заказ\nОформить\nУспех",
                embedding=emb.embed("оформить заказ роутер"),
                step="Оформить",
                expected_result="Успех",
            )
        ]
    )
    parsed = parse_requirements_document(
        "## СИСТЕМА 1\n1. Настроить продукты роутера\n"
    )
    leaf = parsed.leaves[0]
    prompt = rag.enrich_leaf_prompt(
        leaf, user_id="u1", document_id="current", task_name="Demo"
    )
    assert "СИСТЕМА 1" in prompt or "Настроить" in prompt
    assert "Примеры шаблонов" in prompt or "Позитив" in prompt
    assert "Related requirements" in prompt or "СИСТЕМА 2" in prompt


def test_chat_returns_citations(monkeypatch):
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb, chat_top_k=3)
    rag.index_document_text(
        user_id="u1",
        document_id="d1",
        text="## Основные требования\nРассрочка на 24 месяца для Wi-Fi роутера.\n",
    )

    def fake_ai(system: str, user: str) -> str:
        assert "Фрагменты требований" in user
        return "Срок рассрочки — 24 месяца."

    out = rag.chat(user_id="u1", question="Какой срок рассрочки?", ai_generate=fake_ai)
    assert "24" in out["answer"]
    assert out["citations"]
    assert out["citations"][0]["document_id"] == "d1"


def test_replace_for_document_clears_old_chunks():
    docs = MemoryDocumentChunkRepository()
    emb = HashEmbeddingClient(dims=16)
    rag = RagService(
        doc_chunks=docs, case_chunks=MemoryCaseChunkRepository(), embedder=emb
    )
    rag.index_document_text(user_id="u1", document_id="d1", text="## A\ntext one\n")
    rag.index_document_text(user_id="u1", document_id="d1", text="## B\ntext two only\n")
    hits = docs.match(
        user_id="u1",
        query_embedding=emb.embed("text two"),
        match_count=10,
        only_document_id="d1",
    )
    assert hits
    assert all("text one" not in (h.content or "") for h in hits)
