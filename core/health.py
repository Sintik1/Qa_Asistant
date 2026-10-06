"""Build structured health payload for GET /api/health (monitoring)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import httpx
from flask import Flask

from integrations.ai_client import ai_status_dict


def _disk_check(path: Path) -> dict[str, Any]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(path)
        free_mb = round(usage.free / (1024 * 1024), 1)
        ok = usage.free > 50 * 1024 * 1024  # >50 MiB free
        return {
            "ok": ok,
            "path": str(path),
            "free_mb": free_mb,
        }
    except OSError as exc:
        return {"ok": False, "path": str(path), "error": str(exc)[:120]}


def _db_check(app: Flask) -> dict[str, Any]:
    persist = app.extensions.get("persist_mode", "memory")
    if persist != "supabase":
        return {"ok": True, "mode": persist, "ping": "skipped"}

    url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
    key = (os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key or url.startswith("your_") or key.startswith("your_"):
        return {"ok": False, "mode": persist, "ping": "missing_env"}

    try:
        response = httpx.get(
            f"{url}/rest/v1/",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=3.0,
        )
        # 200 or 404 on root are both "reachable"; 401/403 still mean API is up
        ok = response.status_code < 500
        return {
            "ok": ok,
            "mode": persist,
            "ping": "ok" if ok else f"http_{response.status_code}",
            "status_code": response.status_code,
        }
    except httpx.HTTPError as exc:
        return {"ok": False, "mode": persist, "ping": "error", "error": str(exc)[:120]}


def _ai_check() -> dict[str, Any]:
    status = ai_status_dict()
    configured = bool(status.get("configured"))
    return {
        "ok": configured,  # soft: not configured ≠ process down
        "configured": configured,
        "provider": status.get("provider"),
        "model": status.get("model"),
    }


def build_health_payload(app: Flask) -> dict[str, Any]:
    uploads = Path(os.getenv("UPLOADS_DIR") or os.getenv("UPLOAD_DIR") or "uploads")
    emb = app.extensions.get("embedding_settings")
    rag = app.extensions.get("rag_service")

    checks = {
        "app": {"ok": True},
        "disk": _disk_check(uploads),
        "db": _db_check(app),
        "ai": _ai_check(),
    }
    critical_ok = checks["app"]["ok"] and checks["disk"]["ok"]
    # DB soft-fail: supabase unreachable still returns HTTP 200 with status degraded
    overall = "ok" if critical_ok and checks["db"]["ok"] else ("degraded" if critical_ok else "fail")

    return {
        "status": overall,
        "api": "qa-assistant",
        "mode": "hybrid-c",
        "persist": app.extensions.get("persist_mode", "memory"),
        "ai": ai_status_dict(),
        "rag": {
            "enabled": bool(rag and getattr(rag, "enabled", False)),
            "embedding_provider": getattr(emb, "provider", None),
            "embedding_model": getattr(emb, "model", None),
            "embedding_dims": getattr(emb, "dims", None),
        },
        "checks": checks,
    }
