#!/usr/bin/env python3
"""Fail if known-secret-shaped values appear outside gitignored .env."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "node_modules", "uploads", "logs", ".ruff_cache", "dist"}
# Only scan text-ish files
ALLOW_SUFFIX = {".py", ".ts", ".tsx", ".md", ".yml", ".yaml", ".json", ".txt", ".toml", ".example", ".local"}

# High-confidence leakage patterns (never commit these shapes with real values)
PATTERNS = [
    re.compile(r"GOCSPX-[A-Za-z0-9_-]{10,}"),
    re.compile(r"sb_secret_[A-Za-z0-9_]{10,}"),
    re.compile(r"ya29\.[A-Za-z0-9._-]{20,}"),  # Google access tokens
]


def main() -> int:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == ".env" or path.name.endswith(".env"):
            continue
        if path.suffix and path.suffix not in ALLOW_SUFFIX and path.name not in {
            "Dockerfile",
            "ci.yml",
            ".env.example",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in PATTERNS:
            if pat.search(text):
                # allow documentation examples that are clearly placeholders
                if "[REDACTED]" in text or "your_" in text:
                    # still flag if a full-looking secret exists
                    for m in pat.finditer(text):
                        val = m.group(0)
                        if "REDACTED" in val or "your_" in val or val.endswith("…"):
                            continue
                        if len(val) >= 20:
                            hits.append(f"{path.relative_to(ROOT)}: {pat.pattern}")
                            break
                else:
                    hits.append(f"{path.relative_to(ROOT)}: {pat.pattern}")
                    break
    if hits:
        print("Possible secrets outside .env:")
        for h in hits:
            print(" -", h)
        return 1
    print("OK: no high-confidence secret patterns outside .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
