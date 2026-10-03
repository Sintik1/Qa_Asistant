"""Parse AI text into CSV-aligned test case rows."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCase:
    name: str
    step: str
    expected_result: str
    status: str = "Approved"


_CSV_HEADER = re.compile(
    r"^\s*name\s*[,|;]\s*status\s*[,|;]\s*step\s*[,|;]\s*expected",
    re.IGNORECASE,
)


def parse_cases_from_ai_text(text: str) -> list[ParsedCase]:
    """
    Accept:
    - CSV with header Name,Status,Step,Expected Result
    - pipe/semicolon delimited rows
    - fallback: numbered blocks "1. Name / Step / Expected"
    """
    raw = (text or "").strip()
    if not raw:
        return []

    fenced = re.search(r"```(?:csv)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if fenced:
        raw = fenced.group(1).strip()

    csv_cases = _parse_delimited(raw)
    if csv_cases:
        return csv_cases

    return _parse_numbered_blocks(raw)


def _parse_delimited(raw: str) -> list[ParsedCase]:
    # Normalize pipes/semicolons to commas for csv module when header-like.
    sample = raw.splitlines()[0] if raw else ""
    delimiter = ","
    if sample.count("|") >= 3:
        delimiter = "|"
    elif sample.count(";") >= 3:
        delimiter = ";"

    try:
        reader = csv.reader(io.StringIO(raw), delimiter=delimiter)
        rows = [list(r) for r in reader if any(cell.strip() for cell in r)]
    except csv.Error:
        return []

    if not rows:
        return []

    start = 0
    if _CSV_HEADER.search(",".join(rows[0])) or (
        len(rows[0]) >= 3 and rows[0][0].strip().lower() in {"name", "название"}
    ):
        start = 1

    cases: list[ParsedCase] = []
    for row in rows[start:]:
        cells = [c.strip() for c in row]
        if len(cells) < 3:
            continue
        if len(cells) >= 4:
            name, _status, step, expected = cells[0], cells[1], cells[2], cells[3]
            status = _status or "Approved"
        else:
            name, step, expected = cells[0], cells[1], cells[2]
            status = "Approved"
        if not name or not step:
            continue
        cases.append(
            ParsedCase(
                name=name,
                step=step,
                expected_result=expected or "—",
                status=status if status else "Approved",
            )
        )
    return cases


def _parse_numbered_blocks(raw: str) -> list[ParsedCase]:
    blocks = re.split(r"\n\s*(?=\d+[\).]\s+)", raw)
    cases: list[ParsedCase] = []
    for block in blocks:
        line = " ".join(block.strip().splitlines())
        m = re.match(
            r"^\d+[\).]\s*(.+?)(?:\s*[-–:]\s*|\s*/\s*)(.+?)(?:\s*[-–:]\s*|\s*/\s*)(.+)$",
            line,
        )
        if not m:
            continue
        cases.append(
            ParsedCase(
                name=m.group(1).strip(),
                step=m.group(2).strip(),
                expected_result=m.group(3).strip() or "—",
            )
        )
    return cases
