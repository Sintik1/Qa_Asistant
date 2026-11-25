"""Word tables → structured markers used by the TestSites generation prompts.

One table is one block (``TABLE_N_START`` … rows), not one case per row.
"""

from __future__ import annotations


def normalize_cells(cells: list[str]) -> list[str]:
    """Collapse whitespace and drop consecutive duplicates from merged cells."""
    normalized: list[str] = []
    for raw in cells:
        text = " ".join(str(raw or "").replace("\n", " ").replace("\r", " ").split()).strip()
        text = text or "-"
        if not normalized or normalized[-1] != text:
            normalized.append(text)
    return normalized


def format_table_from_rows(
    normalized_rows: list[list[str]],
    *,
    table_number: int = 1,
    table_title: str = "",
) -> str:
    """Render rows as ``TABLE_N_*`` lines wrapped in ``TABLE_BLOCK_*``."""
    if not normalized_rows:
        return ""

    headers = normalized_rows[0]
    data_rows = normalized_rows[1:] if len(normalized_rows) > 1 else []
    n = table_number
    parts = [f"TABLE_BLOCK_BEGIN_{n}", f"TABLE_{n}_START"]
    title = (table_title or "").strip()
    if title:
        parts.append(f"TABLE_{n}_TITLE: {title}")
    parts.append(f"TABLE_{n}_COLUMNS: " + " || ".join(headers))
    if data_rows:
        for idx, row_cells in enumerate(data_rows, start=1):
            parts.append(f"TABLE_{n}_ROW_{idx}: " + " || ".join(row_cells))
    else:
        parts.append(f"TABLE_{n}_ROW_1: " + " || ".join(headers))
    parts.append(f"TABLE_BLOCK_END_{n}")
    return "\n".join(parts)


def infer_table_caption(paragraph_text: str, table_number: int, section_title: str = "") -> str:
    """Short caption from the paragraph immediately above the table."""
    txt = " ".join((paragraph_text or "").split()).strip()
    if txt and len(txt) <= 120 and not txt.endswith((".", ";", "!", "?")):
        return txt.rstrip(":")
    section = " ".join((section_title or "").split()).strip()
    if section:
        return section
    return f"Таблица {table_number}"


def format_docx_table(table: object, table_number: int, table_title: str) -> str:
    """Extract a python-docx table into the marker block."""
    rows: list[list[str]] = []
    for row in table.rows:  # type: ignore[attr-defined]
        cells = normalize_cells([(cell.text or "") for cell in row.cells])
        if any(cell != "-" for cell in cells):
            rows.append(cells)
    return format_table_from_rows(rows, table_number=table_number, table_title=table_title)
