#!/usr/bin/env python3
"""Interactively save OAuth Client ID/Secret into gitignored `.env` (never prints secrets)."""

from __future__ import annotations

import getpass
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

KEYS = (
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "YANDEX_CLIENT_ID",
    "YANDEX_CLIENT_SECRET",
)


def upsert_env(path: Path, updates: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines()
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        m = re.match(r"^([A-Z0-9_]+)=(.*)$", line)
        if m and m.group(1) in updates:
            key = m.group(1)
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    print("Saving OAuth credentials into", ENV_PATH)
    print("Values are not echoed. Leave blank to skip a key.")
    updates: dict[str, str] = {}
    for key in KEYS:
        if key.endswith("_SECRET"):
            value = getpass.getpass(f"{key}: ").strip()
        else:
            value = input(f"{key}: ").strip()
        if value:
            updates[key] = value
    if not updates:
        print("Nothing to save.")
        return 1
    upsert_env(ENV_PATH, updates)
    print(f"Updated {len(updates)} key(s) in .env (gitignored).")
    print("For Google: paste the same Client ID/Secret into Supabase Dashboard → Auth → Google.")
    print(
        "Yandex redirect URI must be:",
        "http://127.0.0.1:5001/api/auth/oauth/yandex/callback",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
