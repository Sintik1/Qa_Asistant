"""RAG index / retrieve / chat / templates (memory + hash embeddings)."""

from __future__ import annotations

from io import BytesIO

from app import create_app


def test_health_reports_rag():
    app = create_app(testing=True)
    res = app.test_client().get("/api/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["rag"]["enabled"] is True
    assert body["rag"]["embedding_provider"] == "hash"


def test_index_on_upload_and_chat():
    application = create_app(testing=True)
    client = application.test_client()
    headers = {"X-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            assert "Фрагменты требований" in user_content
            return "Ответ по требованиям: рассрочка 24 месяца. Источник: Основные требования"

    application.extensions["ai_client"] = FakeAi()

    md = (
        "## Основные требования\n"
        "Реализовать акцию с рассрочкой на 24 месяца для Wi-Fi роутера.\n\n"
        "## СИСТЕМА 1\n"
        "1. Настроить новые продукты\n"
    ).encode("utf-8")
    up = client.post(
        "/api/documents/upload",
        data={"file": (BytesIO(md), "reqs.md")},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert up.status_code == 201, up.get_json()
    doc_id = up.get_json()["document"]["id"]

    chat = client.post(
        "/api/chat",
        json={"question": "Какой срок рассрочки?", "document_id": doc_id},
        headers=headers,
    )
    assert chat.status_code == 200, chat.get_json()
    body = chat.get_json()
    assert "рассроч" in body["answer"].lower()
    assert isinstance(body["citations"], list)
    assert len(body["citations"]) >= 1


def test_templates_and_style_enrich_generate():
    application = create_app(testing=True)
    client = application.test_client()
    headers = {"X-User-Id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"}

    tpl = client.post(
        "/api/rag/templates",
        json={
            "items": [
                {
                    "name": "Негатив: лимит рассрочки",
                    "step": "Превысить лимит долга\nПопытаться купить в рассрочку",
                    "expected_result": "Покупка запрещена",
                    "tags": ["negative", "boundary"],
                    "source_type": "template",
                }
            ]
        },
        headers=headers,
    )
    assert tpl.status_code == 200
    assert tpl.get_json()["indexed"] == 1

    seen_prompts: list[str] = []

    class CapturingAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            seen_prompts.append(user_content)
            return (
                "Name,Status,Step,Expected Result\n"
                "CRM case,Approved,\"1. Do A\n2. Do B\",Ok\n"
            )

    application.extensions["ai_client"] = CapturingAi()

    doc = client.post(
        "/api/documents",
        json={"original_filename": "s.md", "size_bytes": 64},
        headers=headers,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"], "chunk_method": "header"},
        headers=headers,
    ).get_json()

    text = (
        "## 3. CRM\n"
        "1. Доработать таблицу\n"
        "2. Изменить сроки акции\n"
    )
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={"requirements_text": text},
        headers=headers,
    )
    assert gen.status_code == 200, gen.get_json()
    assert seen_prompts
    joined = "\n".join(seen_prompts)
    assert "CRM" in joined
    assert gen.get_json()["run"]["case_count"] >= 1


def test_generate_does_not_auto_index_cases_into_rag():
    """AI output must not poison case_chunks until explicit review index."""
    application = create_app(testing=True)
    client = application.test_client()
    headers = {"X-User-Id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"}

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            return (
                "Name,Status,Step,Expected Result\n"
                "Bad AI case,Approved,Do wrong thing,Wrong ok\n"
            )

    application.extensions["ai_client"] = FakeAi()
    doc = client.post(
        "/api/documents",
        json={"original_filename": "s.md", "size_bytes": 64},
        headers=headers,
    ).get_json()
    run = client.post(
        "/api/runs",
        json={"document_id": doc["id"]},
        headers=headers,
    ).get_json()
    gen = client.post(
        f"/api/runs/{run['id']}/generate",
        json={"requirements_text": "## 1. Auth\n1. Login with email\n"},
        headers=headers,
    )
    assert gen.status_code == 200
    cases = gen.get_json()["items"]
    assert cases

    # Memory case-chunk repo should still be empty for this user until opt-in.
    case_repo = application.extensions["rag_service"]._cases  # noqa: SLF001
    before = case_repo.match(
        user_id=headers["X-User-Id"],
        query_embedding=application.extensions["embedding_client"].embed("login"),
        match_count=10,
        source_types=["approved_case"],
    )
    assert before == []

    indexed = client.post(
        "/api/rag/index-cases",
        json={"case_ids": [cases[0]["id"]]},
        headers=headers,
    )
    assert indexed.status_code == 200
    assert indexed.get_json()["indexed"] == 1
    after = case_repo.match(
        user_id=headers["X-User-Id"],
        query_embedding=application.extensions["embedding_client"].embed("login"),
        match_count=10,
        source_types=["approved_case"],
    )
    assert len(after) >= 1
