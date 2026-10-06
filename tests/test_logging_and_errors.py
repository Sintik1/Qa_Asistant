"""Step 7: structured logging, error codes, AI log analysis."""

from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app
from core.errors import ForbiddenError
from core.log_analyzer import (
    analyze_log_text,
    list_scenarios,
    read_log_tail,
    redact_secrets,
    resolve_scenario,
)
from core.messages import ERROR_MESSAGES
from infrastructure.logging_setup import JsonFormatter
import logging as py_logging


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


def test_json_formatter_includes_service_env_event():
    record = py_logging.LogRecord(
        name="qa_assistant",
        level=py_logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request",
        args=(),
        exc_info=None,
    )
    record.request_id = "r1"
    record.event = "http_request"
    line = JsonFormatter().format(record)
    import json

    data = json.loads(line)
    assert data["level"] == "INFO"
    assert data["service"] == "qa-assistant"
    assert "env" in data
    assert data["event"] == "http_request"
    assert data["request_id"] == "r1"


def test_redact_secrets_strips_jwt_and_bearer():
    raw = (
        'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        "eyJzdWIiOiIxIn0.signature "
        "and sb_secret_abc123XYZ"
    )
    cleaned = redact_secrets(raw)
    assert "eyJ" not in cleaned
    assert "sb_secret_abc123XYZ" not in cleaned
    assert "[REDACTED" in cleaned


def test_scenarios_listed_and_resolved():
    names = list_scenarios()
    assert "general" in names
    assert "auth" in names
    assert resolve_scenario("auth") == "auth"
    with pytest.raises(Exception) as exc:
        resolve_scenario("nope")
    assert getattr(exc.value, "code", None) == "VALIDATION_ERROR"


def test_analyze_logs_scenario_auth_uses_prompt(client):
    c, app = client
    captured: dict[str, str] = {}

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            captured["system"] = system_prompt
            captured["user"] = user_content
            assert "UNAUTHORIZED" in user_content or "401" in user_content
            assert "Bearer" not in user_content or "[REDACTED" in user_content
            return "| симптом | гипотеза | проверка |\n| 401 | нет JWT | login |"

    app.extensions["ai_client"] = FakeAi()
    fixture = Path("tests/fixtures/logs/auth_401.jsonl").read_text(encoding="utf-8")
    # inject a secret line to prove redaction
    fixture += (
        '\n{"msg":"debug Authorization: Bearer '
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aaa.bbb"}\n'
    )
    res = c.post(
        "/api/admin/analyze-logs",
        json={"text": fixture, "scenario": "auth"},
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["scenario"] == "auth"
    assert "JWT" in captured["system"] or "auth" in captured["system"].lower()
    assert "UNAUTHORIZED" in captured["system"] or "401" in captured["system"]
    assert "eyJhbGci" not in captured["user"]
    assert "гипотеза" in body["analysis"] or "JWT" in body["analysis"]


def test_analyze_logs_inline_with_mock_ai(client):
    c, app = client

    class FakeAi:
        def generate(self, system_prompt: str, user_content: str) -> str:
            assert "401" in user_content or "UNAUTHORIZED" in user_content
            return "- Root cause: missing JWT\n- Fix: login again"

    app.extensions["ai_client"] = FakeAi()
    res = c.post(
        "/api/admin/analyze-logs",
        json={"text": '{"level":"WARNING","error_code":"UNAUTHORIZED","status":401}\n'},
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["source"] == "inline"
    assert body["scenario"] == "general"
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
    app.extensions["ai_client"] = type("A", (), {"generate": lambda self, s, u: "ok"})()

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


def test_analyze_logs_requires_admin_token_outside_testing(client, monkeypatch):
    """B2a: without LOG_ANALYZE_ADMIN_TOKEN, non-testing app returns 403."""
    monkeypatch.delenv("LOG_ANALYZE_ADMIN_TOKEN", raising=False)
    monkeypatch.setenv("AUTH_DEV_BYPASS", "1")
    c, app = client
    app.config["TESTING"] = False
    app.extensions["ai_client"] = type("A", (), {"generate": lambda self, s, u: "ok"})()
    res = c.post(
        "/api/admin/analyze-logs",
        json={"text": "x"},
        headers={"X-User-Id": "u1"},
    )
    assert res.status_code == 403
    assert res.get_json()["error"]["code"] == "FORBIDDEN"


def test_security_headers_present(client):
    c, _ = client
    res = c.get("/api/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in (res.headers.get("Permissions-Policy") or "")


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
