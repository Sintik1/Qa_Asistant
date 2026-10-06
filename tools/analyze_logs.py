#!/usr/bin/env python3
"""CLI: analyze local Flask logs (or stdin) with the configured AI provider.

Examples:
  python tools/analyze_logs.py
  python tools/analyze_logs.py --scenario auth --file tests/fixtures/logs/auth_401.jsonl
  python tools/analyze_logs.py --file logs/app.log --max-lines 100
  tail -n 80 logs/app.log | python tools/analyze_logs.py --stdin --scenario ai
  python tools/analyze_logs.py --list-scenarios
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from core.log_analyzer import (
    analyze_log_file,
    analyze_log_text,
    list_scenarios,
)
from integrations.ai_client import build_ai_client, load_ai_settings


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="AI analysis of QA Assistant logs")
    parser.add_argument("--file", type=Path, default=None, help="Path to log file")
    parser.add_argument("--max-lines", type=int, default=200)
    parser.add_argument(
        "--scenario",
        default="general",
        help=f"Analysis scenario: {', '.join(list_scenarios())}",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="Print available scenarios and exit",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read log text from stdin (e.g. pasted Supabase Logs)",
    )
    args = parser.parse_args()

    if args.list_scenarios:
        for name in list_scenarios():
            print(name)
        return 0

    ai = build_ai_client(load_ai_settings())
    if ai is None:
        print("AI client not configured. Set AI_PROVIDER / QA_ASISTANT_* in .env", file=sys.stderr)
        return 2

    try:
        if args.stdin:
            text = sys.stdin.read()
            result = analyze_log_text(text, ai, source="stdin", scenario=args.scenario)
        else:
            result = analyze_log_file(
                ai,
                max_lines=args.max_lines,
                path=args.file,
                scenario=args.scenario,
            )
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"# source: {result.source}")
    print(f"# scenario: {result.scenario}")
    print(f"# lines_used: {result.lines_used}")
    print()
    print(result.analysis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
