"""Unit tests for embeddings, section→index, retrieve helpers."""

from __future__ import annotations

from core.rag_lexical import lexical_overlap
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
    assert out["citations"][0]["source_kind"] == "requirement"


def test_chat_retrieves_indexed_cases_when_no_documents():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb, chat_top_k=3)
    cases.upsert_many(
        [
            IndexCaseChunkCommand(
                user_id="u1",
                source_type="approved_case",
                name="Рассрочка 24 мес",
                content="Рассрочка 24 месяца для Wi-Fi роутера",
                embedding=emb.embed("рассрочка 24 месяца роутер"),
                step="Выбрать рассрочку 24 месяца",
                expected_result="Рассрочка активна",
                test_case_id="case-1",
            )
        ]
    )

    def fake_ai(system: str, user: str) -> str:
        assert "type=case" in user
        assert "24" in user
        return "По кейсу: рассрочка 24 месяца."

    out = rag.chat(user_id="u1", question="Какой срок рассрочки?", ai_generate=fake_ai)
    assert "24" in out["answer"]
    assert out["citations"][0]["source_kind"] == "case"
    assert out["citations"][0]["section_path"] == "Рассрочка 24 мес"


def test_chat_can_skip_cases():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb)
    cases.upsert_many(
        [
            IndexCaseChunkCommand(
                user_id="u1",
                source_type="template",
                name="only-case",
                content="секретный кейс",
                embedding=emb.embed("секретный кейс"),
            )
        ]
    )
    out = rag.chat(
        user_id="u1",
        question="что в кейсе?",
        include_cases=False,
        ai_generate=lambda _s, _u: "should not run",
    )
    assert "не найдено" in out["answer"].lower()
    assert out["citations"] == []


def test_index_keeps_table_markers_and_flags_table():
    docs = MemoryDocumentChunkRepository()
    rag = RagService(
        doc_chunks=docs,
        case_chunks=MemoryCaseChunkRepository(),
        embedder=HashEmbeddingClient(dims=16),
    )
    text = (
        "## 3. Каталог\n"
        "Поля карточки\n"
        "TABLE_BLOCK_BEGIN_1\n"
        "TABLE_1_START\n"
        "TABLE_1_COLUMNS: Поле || Тип\n"
        "TABLE_1_ROW_1: Email || string\n"
        "TABLE_BLOCK_END_1\n"
    )
    assert rag.index_document_text(user_id="u1", document_id="doc-table", text=text) == 1
    stored = next(iter(docs._items.values()))[0]  # noqa: SLF001
    assert "TABLE_1_ROW_1: Email || string" in stored.content
    assert stored.metadata.get("has_table") is True

    def fake_ai(system_prompt: str, user_content: str) -> str:
        assert "TABLE_1_ROW_1: Email || string" in user_content
        return "Поле Email имеет тип string."

    out = rag.chat(
        user_id="u1",
        question="Какой тип у поля Email?",
        document_id="doc-table",
        ai_generate=fake_ai,
    )
    assert "string" in out["answer"]
    assert out["citations"][0]["source_kind"] == "requirement"
    assert "TABLE_1_ROW_1" in out["citations"][0]["preview"]


def test_semantic_chat_keeps_every_page_in_the_same_similarity_band():
    class Semantic:
        semantic = True

        def embed(self, text: str) -> list[float]:
            low = (text or "").lower()
            if "домофон" in low and "заяв" in low:
                return [1.0, 1.0]
            if "домофон" in low:
                return [1.0, 0.99]
            if "заяв" in low:
                return [0.99, 1.0]
            return [0.0, 0.2]

    docs = MemoryDocumentChunkRepository()
    rag = RagService(
        doc_chunks=docs,
        case_chunks=MemoryCaseChunkRepository(),
        embedder=Semantic(),
        chat_top_k=4,
    )
    rag.index_document_text(
        user_id="u1",
        document_id="domofon",
        text="# Проект Домофон\n\n1. Создать заказ\n",
        as_single_chunk=True,
    )
    rag.index_document_text(
        user_id="u1",
        document_id="to",
        text="# Как делается заявка на ТО\n\n1. Создать заявку на ТО\n",
        as_single_chunk=True,
    )
    rag.index_document_text(
        user_id="u1",
        document_id="overview",
        text="# Обзор\n\nПоздоровайтесь с коллегами\n",
        as_single_chunk=True,
    )

    out = rag.chat(
        user_id="u1",
        question="как подключить Домофон и создать заявку на ТО",
        ai_generate=lambda *_args, **_kwargs: "не используется",
    )
    ids = [item["document_id"] for item in out["citations"]]
    assert ids == ["domofon", "to"] or ids == ["to", "domofon"]
    assert "Создать заказ" in out["answer"]
    assert "Создать заявку на ТО" in out["answer"]
    assert "Поздоровайтесь" not in out["answer"]


def test_semantic_chat_shows_the_page_when_the_model_only_names_it():
    class Semantic:
        semantic = True

        def embed(self, text: str) -> list[float]:
            low = (text or "").lower()
            if "домофон" in low:
                return [1.0, 0.0]
            return [0.0, 1.0]

    docs = MemoryDocumentChunkRepository()
    rag = RagService(
        doc_chunks=docs,
        case_chunks=MemoryCaseChunkRepository(),
        embedder=Semantic(),
        chat_top_k=2,
    )
    rag.index_document_text(
        user_id="u1",
        document_id="domofon",
        text="# Проект Домофон\n\n1. Создать заказ\n2. Отправить на исполнение\n",
        as_single_chunk=True,
    )

    out = rag.chat(
        user_id="u1",
        question="Как подключить услугу Домофон",
        ai_generate=lambda *_args, **_kwargs: "не используется",
    )
    assert "1. Создать заказ" in out["answer"]
    assert out["citations"][0]["document_id"] == "domofon"


def test_activator_page_beats_domofon_on_sdp_question():
    question = "куда активатор ходит при подключении SDP"
    domofon = (
        "Инструкция подключения\n"
        "Проверить что подписка активна\n"
        "Проверить подключние в системе"
    )
    activator = "активатор->SDP\n112.000.000:8080\nАктивация"
    assert lexical_overlap(question, activator) > lexical_overlap(question, domofon)


def test_chat_prefers_page_that_shares_question_words():
    docs = MemoryDocumentChunkRepository()
    cases = MemoryCaseChunkRepository()
    emb = HashEmbeddingClient(dims=32)
    rag = RagService(doc_chunks=docs, case_chunks=cases, embedder=emb, chat_top_k=4)
    rag.index_document_text(
        user_id="u1",
        document_id="router",
        text="## Основные требования\nАкция: роутер с рассрочкой на 24 месяца.\n",
    )
    rag.index_document_text(
        user_id="u1",
        document_id="domofon",
        text=(
            "## Проект Домофон\n"
            "Инструкция подключения. Создать заказ. Отправить на исполнение. "
            "Проверить что подписка активна.\n"
        ),
    )
    cases.upsert_many(
        [
            IndexCaseChunkCommand(
                user_id="u1",
                source_type="approved_case",
                name="Заказ по акции",
                content="Заказ нового оборудования по акции недоступен. Рассрочка.",
                embedding=emb.embed("акция рассрочка роутер"),
                step="Проверить акцию",
                expected_result="Запрещено",
                test_case_id="case-router",
            )
        ]
    )

    def fail_ai(system: str, user: str) -> str:
        raise AssertionError(f"chat must quote the page, not call the model: {user[:80]}")

    out = rag.chat(
        user_id="u1",
        question="Как подключить услугу Домофон",
        ai_generate=fail_ai,
    )
    assert out["answer"] == (
        "Инструкция подключения. Создать заказ. Отправить на исполнение. "
        "Проверить что подписка активна."
    )
    assert "рассрочк" not in out["answer"].lower()
    assert out["citations"][0]["document_id"] == "domofon"
    assert all(item["document_id"] == "domofon" for item in out["citations"])
    assert lexical_overlap("подключить", "Инструкция подключения") >= 1


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
