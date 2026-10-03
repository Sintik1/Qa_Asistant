#!/usr/bin/env python3
"""Fully autonomous DB E2E for local QA (no mailbox / no Confirm email click).

Creates a confirmed auth user via Postgres (Supabase SQL is done by the agent MCP
or optional DATABASE_URL), then runs Flask happy path and prints PostgREST checks.

This CLI path uses Auth password grant after SQL seed when credentials are provided
via env; for agent runs prefer MCP execute_sql + this script with QA_E2E_LOGIN_ONLY=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    email = os.getenv("QA_E2E_EMAIL")
    password = os.getenv("QA_E2E_PASSWORD") or "AutoTestPersist123!"
    if not email:
        print(
            "Set QA_E2E_EMAIL(+PASSWORD) after creating a confirmed user "
            "(agent: Supabase MCP SQL insert into auth.users)."
        )
        return 2
    env = os.environ.copy()
    env["QA_E2E_LOGIN_ONLY"] = "1"
    env["QA_E2E_EMAIL"] = email
    env["QA_E2E_PASSWORD"] = password
    api = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5001"
    return subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "live_db_happy_path.py"), api],
        env=env,
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    raise SystemExit(main())
