#!/usr/bin/env python3
"""E2E: Supabase signup → Flask happy path → verify rows in Postgres.

Requires:
  SUPABASE_URL, SUPABASE_ANON_KEY
  Flask with persist=supabase (same env)
  Ollama/AI for generate
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API = (os.getenv("QA_API_BASE") or (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5001")).rstrip("/")
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
ANON = os.getenv("SUPABASE_ANON_KEY") or ""
# Supabase rejects reserved domains like example.com
EMAIL = os.getenv("QA_E2E_EMAIL") or f"qa.persist.{uuid.uuid4().hex[:10]}@gmail.com"
PASSWORD = os.getenv("QA_E2E_PASSWORD") or "TestPersist123!"
LOGIN_ONLY = (os.getenv("QA_E2E_LOGIN_ONLY") or "").strip() == "1"


def main() -> int:
    if not SUPABASE_URL or not ANON:
        print("FAIL: SUPABASE_URL / SUPABASE_ANON_KEY missing")
        return 1

    health = httpx.get(f"{API}/api/health", timeout=30)
    health.raise_for_status()
    persist = health.json().get("persist")
    print(f"health persist={persist}")
    if persist != "supabase":
        print("FAIL: Flask not in supabase persist mode (check SUPABASE_URL/ANON)")
        return 1

    access = None
    user_id = None
    print(f"email={EMAIL}")

    if not LOGIN_ONLY:
        # 1) Signup
        auth = httpx.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": ANON, "Content-Type": "application/json"},
            json={"email": EMAIL, "password": PASSWORD},
            timeout=60,
        )
        print(f"signup HTTP {auth.status_code}")
        if auth.status_code >= 400:
            print(auth.text[:400])
            return 1
        body = auth.json()
        access = body.get("access_token")
        user = body.get("user") or {}
        user_id = user.get("id")
        print(f"user_id={user_id}")
        # brief wait for trigger handle_new_user
        time.sleep(1.5)

        if not access:
            service = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
            if service and user_id and not service.startswith("your_"):
                conf = httpx.put(
                    f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": service,
                        "Authorization": f"Bearer {service}",
                        "Content-Type": "application/json",
                    },
                    json={"email_confirm": True},
                    timeout=60,
                )
                print(f"admin confirm HTTP {conf.status_code}")
            else:
                print(
                    "WARN: email confirm likely required. "
                    "Confirm via SQL/Dashboard or set SUPABASE_SERVICE_ROLE_KEY."
                )

    if not access:
        login = httpx.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": ANON, "Content-Type": "application/json"},
            json={"email": EMAIL, "password": PASSWORD},
            timeout=60,
        )
        print(f"login HTTP {login.status_code}")
        if login.status_code >= 400:
            print(login.text[:400])
            print(
                "FAIL: cannot login. Confirm email or disable Confirm email in Auth settings."
            )
            return 1
        login_body = login.json()
        access = login_body.get("access_token")
        user_id = (login_body.get("user") or {}).get("id") or user_id

    if not access or not user_id:
        print("FAIL: missing access_token / user id")
        return 1
    print(f"user_id={user_id}")

    headers = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json",
        "X-Request-Id": f"db-e2e-{uuid.uuid4()}",
    }

    # 2) settings touch
    settings = httpx.get(f"{API}/api/settings", headers=headers, timeout=30)
    print(f"GET settings HTTP {settings.status_code}")
    if settings.status_code != 200:
        print(settings.text[:400])
        return 1

    # 3) upload
    md = (
        "# Auth requirements\n\n"
        "User can log in with email/password.\n"
        "Wrong password shows an error.\n"
    ).encode("utf-8")
    up = httpx.post(
        f"{API}/api/documents/upload",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": headers["X-Request-Id"]},
        files={"file": ("persist_reqs.md", md, "text/markdown")},
        timeout=60,
    )
    print(f"POST upload HTTP {up.status_code}")
    if up.status_code != 201:
        print(up.text[:500])
        return 1
    up_body = up.json()
    doc_id = up_body["document"]["id"]
    text = up_body["text"]
    print(f"document_id={doc_id} chars={up_body.get('char_count')}")

    # 4) run + generate
    run = httpx.post(
        f"{API}/api/runs",
        headers=headers,
        json={"document_id": doc_id, "chunk_method": "header"},
        timeout=30,
    )
    print(f"POST runs HTTP {run.status_code}")
    if run.status_code != 201:
        print(run.text[:500])
        return 1
    run_id = run.json()["id"]
    print(f"run_id={run_id}")

    gen = httpx.post(
        f"{API}/api/runs/{run_id}/generate",
        headers=headers,
        json={
            "requirements_text": text,
            "task_name": "DB Persist",
            "prompt": "Сгенерируй 2 тест-кейса CSV: Name,Status,Step,Expected Result",
        },
        timeout=300,
    )
    print(f"POST generate HTTP {gen.status_code}")
    if gen.status_code != 200:
        print(gen.text[:500])
        return 1
    cases = gen.json().get("items") or []
    print(f"cases={len(cases)}")
    if len(cases) < 1:
        print("FAIL: no cases persisted via API")
        return 1

    # 5) verify via PostgREST as same user (RLS)
    rest = f"{SUPABASE_URL}/rest/v1"
    rh = {
        "apikey": ANON,
        "Authorization": f"Bearer {access}",
    }
    profile = httpx.get(
        f"{rest}/profiles",
        params={"id": f"eq.{user_id}", "select": "id,display_name"},
        headers=rh,
        timeout=30,
    )
    docs = httpx.get(
        f"{rest}/documents",
        params={"id": f"eq.{doc_id}", "select": "id,status,original_filename"},
        headers=rh,
        timeout=30,
    )
    runs = httpx.get(
        f"{rest}/generation_runs",
        params={"id": f"eq.{run_id}", "select": "id,status,case_count"},
        headers=rh,
        timeout=30,
    )
    tcs = httpx.get(
        f"{rest}/test_cases",
        params={"run_id": f"eq.{run_id}", "select": "id,name"},
        headers=rh,
        timeout=30,
    )
    us = httpx.get(
        f"{rest}/user_settings",
        params={"user_id": f"eq.{user_id}", "select": "user_id,chunk_method"},
        headers=rh,
        timeout=30,
    )

    checks = {
        "profile": profile.status_code == 200 and len(profile.json()) == 1,
        "user_settings": us.status_code == 200 and len(us.json()) == 1,
        "document": docs.status_code == 200 and len(docs.json()) == 1,
        "run": runs.status_code == 200
        and len(runs.json()) == 1
        and runs.json()[0].get("status") == "done",
        "test_cases": tcs.status_code == 200 and len(tcs.json()) >= 1,
    }
    print("DB checks:")
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
        if not ok:
            raw = {
                "profile": profile,
                "user_settings": us,
                "document": docs,
                "run": runs,
                "test_cases": tcs,
            }[name]
            print(f"    HTTP {raw.status_code} body={raw.text[:300]}")

    print(
        f"\nSummary: user={EMAIL} doc={doc_id} run={run_id} "
        f"cases_api={len(cases)} cases_db={len(tcs.json()) if tcs.status_code==200 else 0}"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
