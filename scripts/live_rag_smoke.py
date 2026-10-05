#!/usr/bin/env python3
"""Live RAG smoke against running Flask (AUTH_DEV_BYPASS or real JWT).

Usage:
  AUTH_DEV_BYPASS=1 python scripts/live_rag_smoke.py
  QA_ASSISTANT_API=http://127.0.0.1:5001 QA_ASSISTANT_JWT=... X_USER_ID=... \\
    python scripts/live_rag_smoke.py

Env:
  QA_ASSISTANT_API — Flask base URL (default http://127.0.0.1:5001)
  QA_ASSISTANT_JWT — Supabase access token (required when AUTH_DEV_BYPASS=0)
  X_USER_ID — user uuid (optional if JWT carries sub)
  SUPABASE_URL / SUPABASE_ANON_KEY — used only to seed a reviewed case when
    generate fails (Leopold empty); index-cases still exercises RAG path.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from io import BytesIO

import httpx

API = os.getenv("QA_ASSISTANT_API", "http://127.0.0.1:5001").rstrip("/")
USER = os.getenv("X_USER_ID", "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
TOKEN = os.getenv("QA_ASSISTANT_JWT", "").strip()
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_ANON = (os.getenv("SUPABASE_ANON_KEY") or "").strip()


def headers() -> dict[str, str]:
    h = {"X-User-Id": USER}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def seed_reviewed_case(run_id: str) -> str | None:
    """Insert one approved case via PostgREST when AI generate is unavailable."""
    if not TOKEN or not SUPABASE_URL or not SUPABASE_ANON:
        return None
    case_id = str(uuid.uuid4())
    payload = {
        "id": case_id,
        "run_id": run_id,
        "user_id": USER,
        "name": "Smoke reviewed: рассрочка 24",
        "status": "Approved",
        "step": "1. Открыть акцию\n2. Выбрать рассрочку 24 месяца",
        "expected_result": "Условия рассрочки применены",
        "sort_order": 0,
    }
    res = httpx.post(
        f"{SUPABASE_URL}/rest/v1/test_cases",
        headers={
            "apikey": SUPABASE_ANON,
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=payload,
        timeout=30.0,
    )
    if res.status_code not in (200, 201):
        print("   seed case FAIL", res.status_code, res.text[:300])
        return None
    return case_id


def main() -> int:
    client = httpx.Client(timeout=180.0)
    print("1) health.rag …")
    health = client.get(f"{API}/api/health").json()
    rag = health.get("rag")
    if not rag or not rag.get("enabled"):
        print("FAIL: rag not enabled on server — restart Flask with new code?", health)
        return 1
    print("   OK", rag)

    print("2) upload markdown …")
    md = (
        "## Основные требования\n"
        "Акция: роутер с рассрочкой на 24 месяца.\n\n"
        "## СИСТЕМА 2\n"
        "Заказ нового об-я по акции недоступен.\n"
    ).encode("utf-8")
    up = client.post(
        f"{API}/api/documents/upload",
        headers=headers(),
        files={"file": ("live_rag.md", BytesIO(md), "text/markdown")},
    )
    if up.status_code != 201:
        print("FAIL upload", up.status_code, up.text[:400])
        return 1
    doc_id = up.json()["document"]["id"]
    print("   doc_id", doc_id)

    print("3) templates …")
    tpl = client.post(
        f"{API}/api/rag/templates",
        headers={**headers(), "Content-Type": "application/json"},
        json={
            "items": [
                {
                    "name": "Негатив лимит",
                    "step": "Превысить лимит\nКупить в рассрочку",
                    "expected_result": "Запрещено",
                    "tags": ["negative"],
                    "source_type": "template",
                }
            ]
        },
    )
    if tpl.status_code != 200:
        print("FAIL templates", tpl.status_code, tpl.text[:400])
        return 1
    print("   indexed", tpl.json())

    print("4) chat …")
    chat = client.post(
        f"{API}/api/chat",
        headers={**headers(), "Content-Type": "application/json"},
        json={"question": "Какой срок рассрочки?", "document_id": doc_id},
    )
    if chat.status_code != 200:
        print("FAIL chat", chat.status_code, chat.text[:500])
        return 1
    chat_body = chat.json()
    print("   answer:", (chat_body.get("answer") or "")[:200])
    print("   citations:", len(chat_body.get("citations") or []))
    if not chat_body.get("citations"):
        print("FAIL: expected citations from indexed doc")
        return 1

    print("5) generate + explicit index-cases …")
    run = client.post(
        f"{API}/api/runs",
        headers={**headers(), "Content-Type": "application/json"},
        json={"document_id": doc_id, "chunk_method": "header"},
    )
    if run.status_code not in (200, 201):
        print("FAIL create run", run.status_code, run.text[:400])
        return 1
    run_id = run.json()["id"]
    gen = client.post(
        f"{API}/api/runs/{run_id}/generate",
        headers={**headers(), "Content-Type": "application/json"},
        json={},
    )
    case_ids: list[str] = []
    if gen.status_code == 200:
        items = gen.json().get("items") or []
        print("   cases", len(items), "status", gen.json()["run"]["status"])
        if items:
            case_ids = [items[0]["id"]]
    else:
        print(
            "   generate unavailable (",
            gen.status_code,
            ") — seed reviewed case for index-cases",
        )
        seeded = seed_reviewed_case(run_id)
        if not seeded:
            print("FAIL generate and seed", gen.text[:400])
            return 1
        case_ids = [seeded]
        print("   seeded case", seeded)

    idx = client.post(
        f"{API}/api/rag/index-cases",
        headers={**headers(), "Content-Type": "application/json"},
        json={"case_ids": case_ids},
    )
    if idx.status_code != 200:
        print("FAIL index-cases", idx.status_code, idx.text[:400])
        return 1
    print("   index-cases", idx.json())

    print("\nPASS live RAG smoke")
    print(json.dumps({"doc_id": doc_id, "run_id": run_id, "rag": rag}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
