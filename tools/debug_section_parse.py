#!/usr/bin/env python3
"""Debug hierarchical section parsing and prompt assembly.

Usage:
  python tools/debug_section_parse.py path/to/file.md
  python tools/debug_section_parse.py path/to/file.docx --prompts
  python tools/debug_section_parse.py path/to/file.md --exclude 1,2 --exclude-title приложение

No network. Writes a JSON summary to stdout (and optional prompts dump).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.doc_reader import extract_text  # noqa: E402
from core.prompt_builder import iter_generation_prompts  # noqa: E402
from core.section_parser import ParseOptions, parse_requirements_document  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Requirements file (.md/.docx/.pdf/.txt)")
    parser.add_argument(
        "--exclude",
        default="",
        help="Comma-separated section ids to drop (e.g. 1,2,5.1)",
    )
    parser.add_argument(
        "--exclude-title",
        action="append",
        default=[],
        help="Drop sections whose title contains this substring (repeatable)",
    )
    parser.add_argument(
        "--prompts",
        action="store_true",
        help="Also print per-leaf user prompts",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write JSON debug dump to this file",
    )
    args = parser.parse_args()

    data = args.path.read_bytes()
    extracted = extract_text(args.path.name, data)
    exclude_ids = frozenset(
        x.strip() for x in args.exclude.split(",") if x.strip()
    )
    options = ParseOptions(
        exclude_section_ids=exclude_ids,
        exclude_title_substrings=tuple(args.exclude_title or ()),
    )
    parsed = parse_requirements_document(extracted.text, options=options)
    payload = {
        "source": str(args.path),
        "extracted_chars": extracted.char_count,
        "parse": parsed.to_debug_dict(),
    }
    if args.prompts:
        prompts = iter_generation_prompts(parsed, raw_text_fallback=extracted.text)
        payload["prompts"] = [
            {
                "leaf_number": leaf_no,
                "system_prompt": system[:200] + ("…" if len(system) > 200 else ""),
                "user_prompt": user,
            }
            for system, user, leaf_no in prompts
        ]

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out} (leaves={len(parsed.leaves)})", file=sys.stderr)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
