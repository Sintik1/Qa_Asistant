"""Unit checks for Supabase ↔ domain status mapping and persist mode selection."""

from __future__ import annotations

import os

from app import _build_repositories, create_app
from infrastructure.supabase_store import _DOC_FROM_DB, _DOC_TO_DB, _RUN_FROM_DB, _RUN_TO_DB


def test_document_status_roundtrip_mapping():
    assert _DOC_TO_DB["extracted"] == "parsed"
    assert _DOC_FROM_DB["parsed"] == "extracted"
    assert _DOC_TO_DB["failed"] == "failed"


def test_run_status_roundtrip_mapping():
    assert _RUN_TO_DB["completed"] == "done"
    assert _RUN_FROM_DB["done"] == "completed"
    assert _RUN_TO_DB["generating"] == "calling_ai"


def test_testing_mode_uses_memory(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon")
    *_repos, mode = _build_repositories(testing=True)
    assert mode == "memory"


def test_create_app_reports_persist_mode_memory_when_testing():
    app = create_app(testing=True)
    assert app.extensions["persist_mode"] == "memory"
    res = app.test_client().get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["persist"] == "memory"


def test_create_app_selects_supabase_when_env_present(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("PERSIST_BACKEND", "supabase")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
    *_repos, mode = _build_repositories(testing=False)
    assert mode == "supabase"


def test_persist_backend_memory_forces_memory(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("PERSIST_BACKEND", "memory")
    *_repos, mode = _build_repositories(testing=False)
    assert mode == "memory"
