"""Health payload / monitoring contract (CI/CD ДЗ шаг 6)."""

from __future__ import annotations

from app import create_app


def test_health_includes_checks_block():
    app = create_app(testing=True)
    res = app.test_client().get("/api/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["api"] == "qa-assistant"
    assert body["status"] in {"ok", "degraded", "fail"}
    assert "checks" in body
    assert body["checks"]["app"]["ok"] is True
    assert "disk" in body["checks"]
    assert "db" in body["checks"]
    assert "ai" in body["checks"]
    assert "configured" in body["checks"]["ai"]


def test_health_keyword_for_uptime_robot():
    """UptimeRobot keyword monitor can match a stable public string."""
    app = create_app(testing=True)
    raw = app.test_client().get("/api/health").get_data(as_text=True)
    assert '"api":"qa-assistant"' in raw.replace(" ", "") or '"api": "qa-assistant"' in raw
