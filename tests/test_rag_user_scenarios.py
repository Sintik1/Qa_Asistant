"""End-to-end user scenarios for RAG via Flask test client (memory persist)."""

from __future__ import annotations

from io import BytesIO

from app import create_app


USER = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
HEADERS = {"X-User-Id": USER}


def _app_client():
    application = create_app(testing=True)
    return application, application.test_client()


def _fake_ai_csv(name: str = "Case A"):
    class FakeAi:
        def __init__(self) -> None:
            self.prompts: list[str] = []

        def generate(self, system_prompt: str, user_content: str) -> str:
            self.prompts.append(user_content)
            if "Фрагменты требований" in user_content:
                return "По документу: рассрочка 24 месяца. Источник: Основные требования"
            return (
                "Name,Status,Step,Expected Result\n"
                f"{name},Approved,\"1. Step one\n2. Step two\",Expected ok\n"
            )

    return FakeAi()


def test_scenario_upload_indexes_and_chat_answers():
    app, client = _app_client()
    ai = _fake_ai_csv()
    app.extensions["ai_client"] = ai

    md = (
        "## Основные требования\n"
        "Акция: продажа роутера с рассрочкой на 24 месяца.\n\n"
        "## СИСТЕМА 1\n"
        "1. Настроить продукты оборудования\n"
    ).encode("utf-8")
    up = client.post(
        "/api/documents/upload",
        data={"file": (BytesIO(md), "promo.md")},
        content_type="multipart/form-data",
        headers=HEADERS,
    )
    assert up.status_code == 201, up.get_json()
    doc_id = up.get_json()["document"]["id"]

    # Indexed chunks exist in memory repo
    rag = app.extensions["rag_service"]
    hits = rag._docs.match(  # noqa: SLF001
        user_id=USER,
        query_embedding=app.extensions["embedding_client"].embed("рассрочка 24"),
        match_count=5,
        only_document_id=doc_id,
    )
    assert len(hits) >= 1

    chat = client.post(
        "/api/chat",
        json={"question": "Какой срок рассрочки для роутера?", "document_id": doc_id},
        headers=HEADERS,
    )
    assert chat.status_code == 200, chat.get_json()
    body = chat.get_json()
    assert "24" in body["answer"]
    assert body["citations"]
    assert body["citations"][0]["document_id"] == doc_id


def test_scenario_templates_enrich_generate_prompt():
    app, client = _app_client()
    ai = _fake_ai_csv("CRM leaf")
    app.extensions["ai_client"] = ai

    tpl = client.post(
        "/api/rag/templates",
        json={
            "items": [
                {
                    "name": "Негатив: лимит рассрочки",
                    "step": "Превысить лимит\nКупить в рассрочку",
                    "expected_result": "Запрещено",
                    "tags": ["negative"],
                    "source_type": "template",
                }
            ]
        },
        headers=HEADERS,
    )
    assert tpl.status_code == 200 and tpl.get_json()["indexed"] == 1

    doc = client.post(
        "/api/documents",
        json={"original_filename": "crm.md", "size_bytes": 40},
        headers=HEADERS,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"]},
        headers=HEADERS,
    ).get_json()
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={
            "requirements_text": (
                "## 3. CRM\n1. Доработать таблицу\n2. Изменить сроки акции\n"
            )
        },
        headers=HEADERS,
    )
    assert gen.status_code == 200, gen.get_json()
    joined = "\n".join(ai.prompts)
    assert "CRM" in joined
    assert "Негатив" in joined or "лимит" in joined.lower()
    assert gen.get_json()["run"]["case_count"] >= 1


def test_scenario_multidoc_related_in_generate():
    app, client = _app_client()
    ai = _fake_ai_csv()
    app.extensions["ai_client"] = ai

    # Doc B indexed via upload
    md_b = (
        "## СИСТЕМА 2\nЗаказ нового оборудования по акции недоступен.\n"
    ).encode("utf-8")
    up_b = client.post(
        "/api/documents/upload",
        data={"file": (BytesIO(md_b), "sys2.md")},
        content_type="multipart/form-data",
        headers=HEADERS,
    )
    assert up_b.status_code == 201

    doc_a = client.post(
        "/api/documents",
        json={"original_filename": "sys1.md", "size_bytes": 40},
        headers=HEADERS,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc_a["id"]},
        headers=HEADERS,
    ).get_json()
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={
            "requirements_text": (
                "## СИСТЕМА 1\n1. Настроить акционные продукты роутера\n"
            )
        },
        headers=HEADERS,
    )
    assert gen.status_code == 200
    joined = "\n".join(ai.prompts)
    assert "Related requirements" in joined or "СИСТЕМА 2" in joined


def test_scenario_no_auto_index_then_explicit_index_cases():
    app, client = _app_client()
    app.extensions["ai_client"] = _fake_ai_csv("Reviewed")
    doc = client.post(
        "/api/documents",
        json={"original_filename": "a.md", "size_bytes": 20},
        headers=HEADERS,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"]},
        headers=HEADERS,
    ).get_json()
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={"requirements_text": "## Auth\n1. Login\n"},
        headers=HEADERS,
    )
    assert gen.status_code == 200
    case_id = gen.get_json()["items"][0]["id"]

    case_repo = app.extensions["rag_service"]._cases  # noqa: SLF001
    emb = app.extensions["embedding_client"]
    assert (
        case_repo.match(
            user_id=USER,
            query_embedding=emb.embed("login"),
            match_count=5,
            source_types=["approved_case"],
        )
        == []
    )

    idx = client.post(
        "/api/rag/index-cases",
        json={"case_ids": [case_id]},
        headers=HEADERS,
    )
    assert idx.status_code == 200
    assert idx.get_json()["indexed"] == 1
    assert case_repo.match(
        user_id=USER,
        query_embedding=emb.embed("login"),
        match_count=5,
        source_types=["approved_case"],
    )


def test_scenario_index_by_run_id():
    app, client = _app_client()
    app.extensions["ai_client"] = _fake_ai_csv()
    doc = client.post(
        "/api/documents",
        json={"original_filename": "b.md", "size_bytes": 20},
        headers=HEADERS,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"]},
        headers=HEADERS,
    ).get_json()
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={"requirements_text": "## Pay\n1. Pay invoice\n"},
        headers=HEADERS,
    )
    assert gen.status_code == 200
    idx = client.post(
        "/api/rag/index-cases",
        json={"run_id": run["id"]},
        headers=HEADERS,
    )
    assert idx.status_code == 200
    assert idx.get_json()["indexed"] >= 1


def test_scenario_chat_empty_corpus_message():
    app, client = _app_client()
    app.extensions["ai_client"] = _fake_ai_csv()
    res = client.post(
        "/api/chat",
        json={"question": "Есть ли что-нибудь?"},
        headers=HEADERS,
    )
    assert res.status_code == 200
    assert "не найдено" in res.get_json()["answer"].lower()


def test_scenario_validation_errors():
    app, client = _app_client()
    # App maps ValidationError → 422 (Unprocessable Entity)
    assert client.post(
        "/api/chat", json={"question": "x"}, headers=HEADERS
    ).status_code in {400, 422}
    assert client.post(
        "/api/rag/templates", json={"items": []}, headers=HEADERS
    ).status_code in {400, 422}
    assert client.post(
        "/api/rag/index-cases", json={}, headers=HEADERS
    ).status_code in {400, 422}


def test_health_exposes_rag_block():
    app, client = _app_client()
    body = client.get("/api/health").get_json()
    assert body["rag"]["enabled"] is True
    assert body["rag"]["embedding_dims"] == 768


def test_scenario_hierarchical_numbered_doc_indexes_leaves_and_chats():
    """User flow: large numbered outline → leaf chunks → chat cites section path."""
    app, client = _app_client()
    ai = _fake_ai_csv()
    app.extensions["ai_client"] = ai

    md = (
        "# ТЗ\n"
        "## 1. Общие положения\n"
        "Акция действует 24 месяца.\n\n"
        "## 2. CRM\n"
        "### 2.1. Таблица\n"
        "1. Доработать таблицу заказов\n"
        "2. Добавить колонку срока\n\n"
        "### 2.2. Лимиты\n"
        "1. Проверить лимит рассрочки\n"
    ).encode("utf-8")
    up = client.post(
        "/api/documents/upload",
        data={"file": (BytesIO(md), "hierarchy.md")},
        content_type="multipart/form-data",
        headers=HEADERS,
    )
    assert up.status_code == 201, up.get_json()
    doc_id = up.get_json()["document"]["id"]

    rag = app.extensions["rag_service"]
    emb = app.extensions["embedding_client"]
    hits = rag._docs.match(  # noqa: SLF001
        user_id=USER,
        query_embedding=emb.embed("лимит рассрочки"),
        match_count=10,
        only_document_id=doc_id,
    )
    assert len(hits) >= 2
    paths = " ".join((h.section_path or "") + " " + (h.title or "") for h in hits)
    assert "CRM" in paths or "2." in paths or "Лимит" in paths

    chat = client.post(
        "/api/chat",
        json={"question": "Что проверить по лимитам?", "document_id": doc_id},
        headers=HEADERS,
    )
    assert chat.status_code == 200
    body = chat.get_json()
    assert body["citations"]
    assert any(c.get("document_id") == doc_id for c in body["citations"])
