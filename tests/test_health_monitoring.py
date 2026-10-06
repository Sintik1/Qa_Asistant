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


def test_health_disk_uses_uploads_dir(tmp_path, monkeypatch):
    uploads = tmp_path / "my_uploads"
    monkeypatch.setenv("UPLOADS_DIR", str(uploads))
    monkeypatch.delenv("UPLOAD_DIR", raising=False)
    app = create_app(testing=True)
    body = app.test_client().get("/api/health").get_json()
    assert body["checks"]["disk"]["path"] == str(uploads)
