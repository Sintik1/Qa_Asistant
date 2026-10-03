#!/usr/bin/env python3
"""Live API matrix for Backend DZ step 8 — Full QA.

Run against a local Flask with AUTH_DEV_BYPASS=1 (or real JWT).
Does not print secrets. Writes docs/API_LIVE_TEST_REPORT.md
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001").rstrip("/")
USER = "11111111-1111-4111-8111-111111111111"
FIXTURES = ROOT / "tests" / "fixtures" / "live_qa"
REPORT = ROOT / "docs" / "API_LIVE_TEST_REPORT.md"

results: list[tuple[str, bool, str]] = []


def hdr(**extra: str) -> dict[str, str]:
    h = {"X-User-Id": USER, "X-Request-Id": f"live-{int(time.time()*1000)}"}
    h.update(extra)
    return h


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"- {mark} {name}" + (f" ({detail})" if detail else ""))


def main() -> int:
    # 1 health
    r = httpx.get(f"{BASE}/api/health", timeout=30)
    ok = r.status_code == 200 and r.json().get("status") == "ok"
    record("GET /api/health", ok, f"HTTP {r.status_code}")
    ai = r.json().get("ai") if ok else {}

    # 2 ai ping
    r = httpx.post(
        f"{BASE}/api/ai/ping",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"prompt": "Ответь одним словом: pong"},
        timeout=180,
    )
    ok = r.status_code == 200 and bool(r.json().get("reply"))
    record("POST /api/ai/ping", ok, f"HTTP {r.status_code}; reply={str(r.json().get('reply', ''))[:40]!r}")

    # 3 create document meta
    r = httpx.post(
        f"{BASE}/api/documents",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={
            "original_filename": "login_requirements.md",
            "size_bytes": 120,
            "mime_type": "text/markdown",
        },
        timeout=30,
    )
    ok = r.status_code == 201 and "id" in r.json()
    doc_id = r.json().get("id") if ok else None
    record("POST /api/documents", ok, f"HTTP {r.status_code}")

    # 4 list / get documents
    r = httpx.get(f"{BASE}/api/documents", headers=hdr(), timeout=30)
    ok = r.status_code == 200 and isinstance(r.json().get("items"), list)
    record("GET /api/documents", ok, f"HTTP {r.status_code}")

    if doc_id:
        r = httpx.get(f"{BASE}/api/documents/{doc_id}", headers=hdr(), timeout=30)
        ok = r.status_code == 200 and r.json().get("id") == doc_id
        record("GET /api/documents/<id>", ok, f"HTTP {r.status_code}")
    else:
        record("GET /api/documents/<id>", False, "skipped — no doc_id")

    # 5 upload md
    md_path = FIXTURES / "login_requirements.md"
    with md_path.open("rb") as fh:
        r = httpx.post(
            f"{BASE}/api/documents/upload",
            headers=hdr(),
            files={"file": (md_path.name, fh, "text/markdown")},
            timeout=60,
        )
    ok = r.status_code == 201 and r.json().get("char_count", 0) > 0
    upload_doc = r.json().get("document", {}) if ok else {}
    upload_text = r.json().get("text", "") if ok else ""
    upload_id = upload_doc.get("id")
    record(
        "POST /api/documents/upload (md)",
        ok,
        f"HTTP {r.status_code}; chars={r.json().get('char_count') if r.headers.get('content-type','').startswith('application/json') else '?'}",
    )

    # 5b upload docx
    docx_path = FIXTURES / "checkout_requirements.docx"
    with docx_path.open("rb") as fh:
        r = httpx.post(
            f"{BASE}/api/documents/upload",
            headers=hdr(),
            files={
                "file": (
                    docx_path.name,
                    fh,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            timeout=60,
        )
    ok = r.status_code == 201 and r.json().get("char_count", 0) > 0
    record(
        "POST /api/documents/upload (docx)",
        ok,
        f"HTTP {r.status_code}; chars={r.json().get('char_count') if r.ok else r.text[:120]}",
    )

    # 6 create run
    run_doc = upload_id or doc_id
    r = httpx.post(
        f"{BASE}/api/runs",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"document_id": run_doc, "chunk_method": "header"},
        timeout=30,
    )
    ok = r.status_code == 201 and "id" in r.json()
    run_id = r.json().get("id") if ok else None
    record("POST /api/runs", ok, f"HTTP {r.status_code}")

    # 7 list/get runs
    r = httpx.get(f"{BASE}/api/runs", headers=hdr(), timeout=30)
    ok = r.status_code == 200 and isinstance(r.json().get("items"), list)
    record("GET /api/runs", ok, f"HTTP {r.status_code}")

    if run_id:
        r = httpx.get(f"{BASE}/api/runs/{run_id}", headers=hdr(), timeout=30)
        ok = r.status_code == 200 and r.json().get("id") == run_id
        record("GET /api/runs/<id>", ok, f"HTTP {r.status_code}")
    else:
        record("GET /api/runs/<id>", False, "skipped")

    # 8 generate
    if run_id:
        r = httpx.post(
            f"{BASE}/api/runs/{run_id}/generate",
            headers=hdr(**{"Content-Type": "application/json"}),
            json={
                "requirements_text": upload_text
                or md_path.read_text(encoding="utf-8"),
                "task_name": "Авторизация",
                "prompt": "Сгенерируй 2–3 тест-кейса в CSV: Name,Status,Step,Expected Result",
            },
            timeout=300,
        )
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        items = body.get("items") or []
        ok = r.status_code == 200 and len(items) >= 1
        record(
            "POST /api/runs/<id>/generate",
            ok,
            f"HTTP {r.status_code}; cases={len(items)}; err={body.get('error')}",
        )
        case_id = items[0]["id"] if items else None
    else:
        case_id = None
        record("POST /api/runs/<id>/generate", False, "skipped")

    # 9 test-cases list
    if run_id:
        r = httpx.get(f"{BASE}/api/runs/{run_id}/test-cases", headers=hdr(), timeout=30)
        items = r.json().get("items") if r.ok else []
        ok = r.status_code == 200 and isinstance(items, list) and len(items) >= 1
        record("GET /api/runs/<id>/test-cases", ok, f"HTTP {r.status_code}; n={len(items) if isinstance(items, list) else 0}")
        if not case_id and items:
            case_id = items[0].get("id")
    else:
        record("GET /api/runs/<id>/test-cases", False, "skipped")

    # 10 patch case
    if case_id:
        r = httpx.patch(
            f"{BASE}/api/test-cases/{case_id}",
            headers=hdr(**{"Content-Type": "application/json"}),
            json={"step": "1. Open login page\n2. Enter credentials"},
            timeout=30,
        )
        ok = r.status_code == 200 and "Open login" in (r.json().get("step") or "")
        record("PATCH /api/test-cases/<id>", ok, f"HTTP {r.status_code}")
    else:
        record("PATCH /api/test-cases/<id>", False, "skipped — no case")

    # 11 settings
    r = httpx.get(f"{BASE}/api/settings", headers=hdr(), timeout=30)
    ok = r.status_code == 200 and "chunk_size" in r.json()
    record("GET /api/settings", ok, f"HTTP {r.status_code}")

    r = httpx.patch(
        f"{BASE}/api/settings",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"chunk_size": 3500, "chunk_method": "header"},
        timeout=30,
    )
    ok = r.status_code == 200 and r.json().get("chunk_size") == 3500
    record("PATCH /api/settings", ok, f"HTTP {r.status_code}")

    # 12 analyze-logs
    r = httpx.post(
        f"{BASE}/api/admin/analyze-logs",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={
            "text": '{"level":"ERROR","msg":"sample","request_id":"demo"}\n'
            '{"level":"INFO","msg":"ok"}',
            "max_lines": 50,
        },
        timeout=180,
    )
    ok = r.status_code == 200 and bool(r.json().get("analysis"))
    record(
        "POST /api/admin/analyze-logs",
        ok,
        f"HTTP {r.status_code}; keys={list(r.json().keys()) if r.ok else r.text[:80]}",
    )

    # --- negatives ---
    r = httpx.get(
        f"{BASE}/api/runs",
        headers={"X-Skip-Auth": "1", "X-Request-Id": "neg-401"},
        timeout=30,
    )
    ok = r.status_code == 401 and r.json().get("error", {}).get("code") == "UNAUTHORIZED"
    record("GET /api/runs without auth → 401", ok, f"HTTP {r.status_code}")

    r = httpx.post(
        f"{BASE}/api/documents",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"original_filename": "virus.exe", "size_bytes": 10},
        timeout=30,
    )
    code = (r.json().get("error") or {}).get("code") if r.headers.get("content-type", "").startswith("application/json") else None
    ok = r.status_code == 422 and code in {"INVALID_FORMAT", "VALIDATION_ERROR"}
    record("POST /api/documents invalid format → 422", ok, f"HTTP {r.status_code}; code={code}")

    with (FIXTURES / "malware.exe").open("rb") as fh:
        r = httpx.post(
            f"{BASE}/api/documents/upload",
            headers=hdr(),
            files={"file": ("malware.exe", fh, "application/octet-stream")},
            timeout=30,
        )
    code = (r.json().get("error") or {}).get("code") if r.headers.get("content-type", "").startswith("application/json") else None
    ok = r.status_code in {400, 422} and code in {"INVALID_FORMAT", "VALIDATION_ERROR"}
    record("POST /api/documents/upload exe → reject", ok, f"HTTP {r.status_code}; code={code}")

    r = httpx.post(
        f"{BASE}/api/documents",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"original_filename": "huge.md", "size_bytes": 200 * 1024 * 1024},
        timeout=30,
    )
    code = (r.json().get("error") or {}).get("code") if r.headers.get("content-type", "").startswith("application/json") else None
    ok = r.status_code == 422 and code in {"FILE_TOO_LARGE", "VALIDATION_ERROR"}
    record("POST /api/documents too large → 422", ok, f"HTTP {r.status_code}; code={code}")

    r = httpx.patch(
        f"{BASE}/api/test-cases/00000000-0000-4000-8000-000000000099",
        headers=hdr(**{"Content-Type": "application/json"}),
        json={"step": "x"},
        timeout=30,
    )
    ok = r.status_code == 404
    record("PATCH /api/test-cases/<missing> → 404", ok, f"HTTP {r.status_code}")

    # delete run
    if run_id:
        r = httpx.delete(f"{BASE}/api/runs/{run_id}", headers=hdr(), timeout=30)
        ok = r.status_code == 204
        record("DELETE /api/runs/<id>", ok, f"HTTP {r.status_code}")
        r = httpx.get(f"{BASE}/api/runs/{run_id}", headers=hdr(), timeout=30)
        ok = r.status_code == 404
        record("GET deleted run → 404", ok, f"HTTP {r.status_code}")
    else:
        record("DELETE /api/runs/<id>", False, "skipped")
        record("GET deleted run → 404", False, "skipped")

    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    lines = [
        "# Live API test report",
        f"Date: {now}",
        f"Base: `{BASE}`",
        f"AI: `{json.dumps(ai, ensure_ascii=False)}`",
        "",
    ]
    for name, ok, detail in results:
        lines.append(f"- {'PASS' if ok else 'FAIL'} {name}" + (f" ({detail})" if detail else ""))
    lines.append("")
    lines.append(f"## Summary: pass={passed} fail={failed}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSummary: pass={passed} fail={failed}")
    print(f"Report: {REPORT}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
