"""Step 7: structured logging, error codes, AI log analysis."""

from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app
from core.errors import ForbiddenError
from core.log_analyzer import analyze_log_text, read_log_tail
from core.messages import ERROR_MESSAGES


@pytest.fixture()
def client():
    application = create_app(testing=True)
    return application.test_client(), application


def test_request_id_header_echo(client):
    c, _ = client
    res = c.get("/api/health", headers={"X-Request-Id": "req-test-1"})
    assert res.status_code == 200
    assert res.headers.get("X-Request-Id") == "req-test-1"


def test_unauthorized_includes_request_id(client):
    c, _ = client
    res = c.get("/api/runs", headers={"X-Skip-Auth": "1", "X-Request-Id": "auth-miss"})
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"] == ERROR_MESSAGES["UNAUTHORIZED"]
    assert body["error"]["request_id"] == "auth-miss"


def test_forbidden_contract(client):
    c, _ = client
    res = c.get("/api/__test__/forbidden", headers={"X-User-Id": "u1"})
    assert res.status_code == 403
    body = res.get_json()
    assert body["error"]["code"] == "FORBIDDEN"
    assert body["error"]["message"] == ERROR_MESSAGES["FORBIDDEN"]
    assert "request_id" in body["error"]


def test_internal_error_contract(client):
    c, _ = client
    res = c.get("/api/__test__/internal", headers={"X-User-Id": "u1"})
    assert res.status_code == 500
    body = res.get_json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["message"] == ERROR_MESSAGES["INTERNAL_ERROR"]


def test_app_error_is_logged(client):
    import logging

    c, _ = client
    records: list[logging.LogRecord] = []

    class _Mem(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = _Mem()
    log = logging.getLogger("qa_assistant")
    log.addHandler(handler)
    try:
        res = c.get("/api/runs", headers={"X-Skip-Auth": "1"})
    finally:
        log.removeHandler(handler)
    assert res.status_code == 401
    assert any("app_error" in r.getMessage() for r in records)
    assert any(getattr(r, "error_code", None) == "UNAUTHORIZED" for r in records)


def test_analyze_logs_inline_with_mock_ai(client):
    c, app = client

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            assert "401" in user_content or "UNAUTHORIZED" in user_content
            return "- Root cause: missing JWT\n- Fix: login again"

    app.extensions["ai_client"] = FakeAi()
    res = c.post(
        "/api/admin/analyze-logs",
        json={
            "text": '{"level":"WARNING","error_code":"UNAUTHORIZED","status":401}\n'
        },
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["source"] == "inline"
    assert body["lines_used"] == 1
    assert "JWT" in body["analysis"]


def test_analyze_logs_disabled(client, monkeypatch):
    monkeypatch.setenv("LOG_ANALYZE_ENABLED", "0")
    c, _ = client
    res = c.post(
        "/api/admin/analyze-logs",
        json={"text": "line"},
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "FORBIDDEN"


def test_analyze_logs_admin_token(client, monkeypatch):
    monkeypatch.setenv("LOG_ANALYZE_ADMIN_TOKEN", "secret-admin")
    c, app = client
    app.extensions["ai_client"] = type(
        "A", (), {"generate": lambda self, s, u: "ok"}
    )()

    denied = c.post(
        "/api/admin/analyze-logs",
        json={"text": "x"},
        headers={"X-User-Id": "u1"},
    )
    assert denied.status_code == 403

    ok = c.post(
        "/api/admin/analyze-logs",
        json={"text": "x"},
        headers={"X-User-Id": "u1", "X-Admin-Token": "secret-admin"},
    )
    assert ok.status_code == 200


def test_read_log_tail(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text("a\nb\nc\n", encoding="utf-8")
    assert read_log_tail(log, max_lines=2) == "b\nc"


def test_analyze_log_text_empty_ai():
    with pytest.raises(Exception) as exc:
        analyze_log_text("line", None)
    assert getattr(exc.value, "code", None) == "MISSING_TOKEN"


def test_forbidden_error_dataclass():
    err = ForbiddenError()
    assert err.status_code == 403
    assert err.to_dict()["error"]["code"] == "FORBIDDEN"
