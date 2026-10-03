"""Extract plain text from requirements documents (PDF / DOCX / MD / TXT)."""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from core.errors import ValidationError
from core.messages import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    extension: str
    char_count: int
    page_or_part_count: int | None = None


def extension_of(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload_meta(filename: str, size_bytes: int) -> str:
    ext = extension_of(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(code="INVALID_FORMAT")
    if size_bytes <= 0:
        raise ValidationError(code="EMPTY_FILE")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValidationError(code="FILE_TOO_LARGE")
    return ext


def extract_text(filename: str, data: bytes) -> ExtractedDocument:
    """Parse bytes into UTF-8 text. Raises ValidationError with TZ codes."""
    if not data:
        raise ValidationError(code="EMPTY_FILE")
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise ValidationError(code="FILE_TOO_LARGE")

    ext = validate_upload_meta(filename, len(data))
    try:
        if ext == ".md":
            text, parts = _extract_plain(data)
        elif ext == ".pdf":
            text, parts = _extract_pdf(data)
        elif ext == ".docx":
            text, parts = _extract_docx(data)
        elif ext == ".doc":
            text, parts = _extract_doc(data)
        else:
            raise ValidationError(code="INVALID_FORMAT")
    except ValidationError:
        raise
    except Exception as exc:  # noqa: BLE001 — map lib failures to TZ code
        raise ValidationError(code="CORRUPT_FILE") from exc

    cleaned = _normalize_text(text)
    if not cleaned:
        raise ValidationError(code="EMPTY_FILE")
    if len(cleaned) < 8:
        raise ValidationError(code="NO_REQUIREMENTS")

    return ExtractedDocument(
        text=cleaned,
        extension=ext,
        char_count=len(cleaned),
        page_or_part_count=parts,
    )


def _normalize_text(text: str) -> str:
    lines = [ln.rstrip() for ln in (text or "").replace("\r\n", "\n").split("\n")]
    # Collapse 3+ blank lines to one blank line.
    out: list[str] = []
    blank = 0
    for ln in lines:
        if ln.strip():
            blank = 0
            out.append(ln)
        else:
            blank += 1
            if blank <= 1:
                out.append("")
    return "\n".join(out).strip()


def _extract_plain(data: bytes) -> tuple[str, int | None]:
    for encoding in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return data.decode(encoding), None
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), None


def _extract_pdf(data: bytes) -> tuple[str, int | None]:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    if getattr(reader, "is_encrypted", False):
        try:
            ok = reader.decrypt("")
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(code="CORRUPT_FILE") from exc
        if ok == 0:
            raise ValidationError(code="CORRUPT_FILE")

    parts: list[str] = []
    for page in reader.pages:
        try:
            chunk = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            chunk = ""
        if chunk.strip():
            parts.append(chunk)
    return "\n\n".join(parts), len(reader.pages)


def _extract_docx(data: bytes) -> tuple[str, int | None]:
    from docx import Document

    # python-docx expects a seekable file-like object.
    document = Document(io.BytesIO(data))
    blocks: list[str] = []
    for para in document.paragraphs:
        t = (para.text or "").strip()
        if t:
            blocks.append(t)
    for table in document.tables:
        for row in table.rows:
            cells = [ (c.text or "").strip() for c in row.cells ]
            cells = [c for c in cells if c]
            if cells:
                blocks.append(" | ".join(cells))
    return "\n".join(blocks), len(document.paragraphs)


def _extract_doc(data: bytes) -> tuple[str, int | None]:
    """
    Legacy .doc: try OOXML (misnamed docx). True OLE .doc needs LibreOffice /
    antiword — not available in this MVP → CORRUPT_FILE.
    """
    if zipfile.is_zipfile(io.BytesIO(data)):
        return _extract_docx(data)
    raise ValidationError(code="CORRUPT_FILE")
