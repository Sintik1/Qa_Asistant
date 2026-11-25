#!/usr/bin/env python3
"""Ping (and optionally restore) the Free-tier Supabase project so Auth DNS stays live.

Free projects pause after ~7 days idle → subdomain NXDOMAIN → UI «Failed to fetch».

Usage (from repo root, with .env loaded):

  python3 scripts/supabase_keepalive.py
  python3 scripts/supabase_keepalive.py --restore

Env:
  SUPABASE_URL / VITE_SUPABASE_URL
  SUPABASE_ANON_KEY / VITE_SUPABASE_ANON_KEY
  SUPABASE_ACCESS_TOKEN  — Management API PAT (needed for --restore)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REF_FALLBACK = "revyywfeeqdmlgrbakpj"
ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, val = raw.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        os.environ.setdefault(key, val)


def _project_ref(url: str) -> str:
    host = url.replace("https://", "").replace("http://", "").split("/")[0]
    if host.endswith(".supabase.co"):
        return host.split(".")[0]
    return REF_FALLBACK


def _http_json(method: str, url: str, headers: dict[str, str], body: bytes | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.getcode(), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 — script: report any transport error
        return 0, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore", action="store_true", help="POST Management API restore if paused")
    args = parser.parse_args()

    _load_dotenv(ROOT / ".env")
    _load_dotenv(ROOT / "qa-assistant" / ".env.local")

    url = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL") or "").rstrip("/")
    anon = os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY") or ""
    token = os.getenv("SUPABASE_ACCESS_TOKEN") or ""
    ref = _project_ref(url) if url else REF_FALLBACK

    if args.restore:
        if not token:
            print(
                "Need SUPABASE_ACCESS_TOKEN (Dashboard → Account → Access Tokens, "
                "permission project_admin_write).",
                file=sys.stderr,
            )
            print(f"Or restore in UI: https://supabase.com/dashboard/project/{ref}")
            return 2
        code, body = _http_json(
            "POST",
            f"https://api.supabase.com/v1/projects/{ref}/restore",
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            b"{}",
        )
        print(f"restore HTTP {code}: {body[:400]}")
        if code not in {200, 201, 202}:
            return 1

    if not url or not anon:
        print("Need SUPABASE_URL and SUPABASE_ANON_KEY to ping REST.", file=sys.stderr)
        return 2

    ping = f"{url}/rest/v1/documents?select=id&limit=1"
    code, body = _http_json(
        "GET",
        ping,
        {
            "apikey": anon,
            "Authorization": f"Bearer {anon}",
            "Accept": "application/json",
        },
    )
    print(f"ping HTTP {code}: {body[:200]}")
    if code == 0:
        print("Transport failed (paused NXDOMAIN / VPN). Restore the project first.", file=sys.stderr)
        return 1
    if code >= 500:
        return 1
    # 401/403 still prove DNS+TLS are alive (Auth host is up).
    print(json.dumps({"ok": True, "status": code, "ref": ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
