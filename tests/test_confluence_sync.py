"""Confluence space → document RAG (HTTP mocked, no live token)."""

from __future__ import annotations

from dataclasses import dataclass

from app import create_app
from integrations.confluence_client import html_to_text


def test_html_to_text_keeps_headings():
    html = "<h1>Каталог</h1><p>Поле <b>Email</b> имеет тип string.</p><script>secret()</script>"
    text = html_to_text(html)
    assert text.startswith("# Каталог")
    assert "**Email**" in text
    assert "string" in text
    assert "secret" not in text


def test_html_to_text_keeps_ordered_list():
    html = (
        "<p>Инструкция подключения</p>"
        "<ol><li><p>Создать заказ</p></li><li><p>Отправить на исполнение</p></li></ol>"
    )
    text = html_to_text(html)
    assert "Инструкция подключения" in text
    assert "1. Создать заказ" in text
    assert "2. Отправить на исполнение" in text


def test_html_to_text_keeps_a_table():
    html = (
        "<table><tr><th><p><strong>Система</strong></p></th><th><p>ip и порт</p></th></tr>"
        "<tr><td><p>активатор-&gt;SDP</p></td><td><p>112.000.000:8080</p></td></tr>"
        "<tr><td><p>активатор-&gt;CRM</p></td>"
        "<td><p>Активация</p><p>Деактивация</p></td></tr></table>"
    )
    text = html_to_text(html)
    assert "| **Система** | ip и порт |" in text
    assert "| --- | --- |" in text
    assert "| активатор->SDP | 112.000.000:8080 |" in text
    assert "Активация<br>Деактивация" in text


def test_html_to_text_keeps_empty_paragraphs():
    html = "<p>Здесь информация по Лицей</p><p>Подключение происходит через CRM и ЛК</p><p /><p>Сервисы которые используются</p>"
    text = html_to_text(html)
    assert "Здесь информация по Лицей\nПодключение происходит через CRM и ЛК\n\nСервисы которые используются" in text


@dataclass
class _Page:
    page_id: str
    title: str
    version: int
    html: str
    url: str


class _FakeConfluence:
    def __init__(self) -> None:
        self.settings = type("S", (), {"space_key": "QA"})()
        self.calls = 0

    def list_pages(self) -> list[_Page]:
        self.calls += 1
        return [
            _Page(
                page_id="99",
                title="Рассрочка",
                version=3,
                html="<h2>Условия</h2><p>Срок рассрочки 24 месяца для Wi-Fi роутера.</p>",
                url="https://wiki.example/spaces/QA/pages/99",
            )
        ]


def test_sync_indexes_page_and_skips_same_version(monkeypatch):
    app = create_app(testing=True)
    monkeypatch.setenv("EMBEDDING_MODEL", "")
    client = _FakeConfluence()
    app.extensions["confluence_client"] = client
    headers = {"X-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}
    api = app.test_client()

    first = api.post("/api/rag/confluence/sync", headers=headers)
    assert first.status_code == 200, first.get_json()
    body = first.get_json()
    assert body["space"] == "QA"
    assert body["indexed"] == 1
    assert body["skipped"] == 0

    docs = api.get("/api/documents", headers=headers)
    assert docs.status_code == 200
    items = docs.get_json()["items"]
    assert len(items) == 1
    assert items[0]["storage_path"] == "confluence/QA/99@v3+page-blocks"
    assert items[0]["status"] == "extracted"

    class Answer:
        def generate(self, system_prompt: str, user_content: str) -> str:
            assert "24 месяца" in user_content
            return "Срок 24 месяца."

    app.extensions["ai_client"] = Answer()
    chat = api.post(
        "/api/chat",
        json={"question": "Какой срок рассрочки?", "include_cases": False},
        headers=headers,
    )
    assert chat.status_code == 200, chat.get_json()
    citation = chat.get_json()["citations"][0]
    assert citation["url"] == "https://wiki.example/spaces/QA/pages/99"
    answer = chat.get_json()["answer"]
    assert "24" in answer
    assert "## Условия" in answer

    second = api.post("/api/rag/confluence/sync", headers=headers)
    assert second.status_code == 200
    assert second.get_json()["indexed"] == 0
    assert second.get_json()["skipped"] == 1


def test_sync_without_config_is_503(monkeypatch):
    app = create_app(testing=True)
    app.extensions["confluence_client"] = None
    # create_app loads .env, so clear the keys after that.
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "")
    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "")
    monkeypatch.setenv("CONFLUENCE_SPACE_KEY", "")
    res = app.test_client().post(
        "/api/rag/confluence/sync",
        headers={"X-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    assert res.status_code == 503
    assert "CONFLUENCE_BASE_URL" in res.get_json()["error"]["message"]
