#!/usr/bin/env python3
"""CLI: analyze local Flask logs (or stdin) with the configured AI provider.

Examples:
  python tools/analyze_logs.py
  python tools/analyze_logs.py --file logs/app.log --max-lines 100
  tail -n 80 logs/app.log | python tools/analyze_logs.py --stdin
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from core.log_analyzer import analyze_log_file, analyze_log_text
from integrations.ai_client import build_ai_client, load_ai_settings


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="AI analysis of QA Assistant logs")
    parser.add_argument("--file", type=Path, default=None, help="Path to log file")
    parser.add_argument("--max-lines", type=int, default=200)
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read log text from stdin (e.g. pasted Supabase Logs)",
    )
    args = parser.parse_args()

    ai = build_ai_client(load_ai_settings())
    if ai is None:
        print("AI client not configured. Set AI_PROVIDER / QA_ASISTANT_* in .env", file=sys.stderr)
        return 2

    try:
        if args.stdin:
            text = sys.stdin.read()
            result = analyze_log_text(text, ai, source="stdin")
        else:
            result = analyze_log_file(ai, max_lines=args.max_lines, path=args.file)
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"# source: {result.source}")
    print(f"# lines_used: {result.lines_used}")
    print()
    print(result.analysis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
