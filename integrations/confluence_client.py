"""Confluence Cloud/DC reader. Token stays in the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from core.errors import AppError


@dataclass(frozen=True)
class ConfluencePage:
    page_id: str
    title: str
    version: int
    html: str
    url: str


@dataclass(frozen=True)
class ConfluenceSettings:
    base_url: str
    email: str
    api_token: str
    space_key: str
    max_pages: int = 25

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_token and self.space_key)


class _HtmlToText(HTMLParser):
    """Confluence storage HTML → Markdown (headings, lists, emphasis, links)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip = 0
        self._lists: list[dict[str, int | str]] = []
        self._marks: list[str] = []
        self._table: list[list[str]] | None = None
        self._cell: list[str] | None = None
        self._para_empty = False

    def _newline(self) -> None:
        if self._parts and not self._parts[-1].endswith("\n"):
            self._parts.append("\n")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        attr = {key.lower(): value or "" for key, value in attrs}
        if name in {"script", "style", "ac:parameter"}:
            self._skip += 1
            return
        if self._skip:
            return
        if name == "table":
            self._newline()
            self._table = []
            self._cell = None
            return
        if self._table is not None:
            self._start_table_tag(name)
            return
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._newline()
            self._parts.append("#" * int(name[1]) + " ")
        elif name == "ol":
            self._newline()
            start = int(attr["start"]) if str(attr.get("start") or "").isdigit() else 1
            self._lists.append({"kind": "ol", "n": start - 1})
        elif name == "ul":
            self._newline()
            self._lists.append({"kind": "ul", "n": 0})
        elif name == "li":
            self._newline()
            if self._lists and self._lists[-1]["kind"] == "ol":
                self._lists[-1]["n"] = int(self._lists[-1]["n"]) + 1
                self._parts.append(f"{self._lists[-1]['n']}. ")
            else:
                self._parts.append("- ")
        elif name == "br":
            self._newline()
        elif name == "p" and not self._lists:
            self._newline()
            self._para_empty = True
        elif name in {"div", "tr"}:
            self._newline()
        elif name in {"td", "th"}:
            self._parts.append(" | ")
        elif name in {"strong", "b"}:
            self._parts.append("**")
            self._marks.append("**")
        elif name in {"em", "i"}:
            self._parts.append("*")
            self._marks.append("*")
        elif name == "code":
            self._parts.append("`")
            self._marks.append("`")
        elif name == "a":
            href = attr.get("href") or ""
            self._parts.append("[")
            self._marks.append(f"]({href})" if href else "]")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name in {"script", "style", "ac:parameter"} and self._skip:
            self._skip -= 1
            return
        if self._skip:
            return
        if self._table is not None:
            self._end_table_tag(name)
            return
        if name in {"ol", "ul"} and self._lists:
            self._lists.pop()
            self._newline()
        elif name == "p" and self._para_empty and not self._lists:
            self._parts.append("\n")
            self._para_empty = False
        elif name in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._para_empty = False
            self._newline()
        elif name in {"strong", "b", "em", "i", "code", "a"} and self._marks:
            self._parts.append(self._marks.pop())

    def handle_data(self, data: str) -> None:
        if self._skip or not data:
            return
        if data.strip():
            self._para_empty = False
        if self._cell is not None:
            self._cell.append(data)
            return
        if self._table is not None:
            return
        self._parts.append(data)

    def _start_table_tag(self, name: str) -> None:
        if name == "tr":
            self._table.append([])  # type: ignore[union-attr]
        elif name in {"td", "th"}:
            self._cell = []
        elif name == "p" and self._cell:
            self._cell.append("<br>")
        elif name in {"strong", "b"} and self._cell is not None:
            self._cell.append("**")
        elif name in {"em", "i"} and self._cell is not None:
            self._cell.append("*")
        elif name == "br" and self._cell is not None:
            self._cell.append("<br>")

    def _end_table_tag(self, name: str) -> None:
        if name == "table":
            self._emit_table()
            self._table = None
            self._cell = None
            return
        if name in {"strong", "b"} and self._cell is not None:
            self._cell.append("**")
        elif name in {"em", "i"} and self._cell is not None:
            self._cell.append("*")
        elif name in {"td", "th"} and self._cell is not None and self._table:
            text = "".join(self._cell).replace("|", "\\|").strip()
            self._table[-1].append(text)
            self._cell = None

    def _emit_table(self) -> None:
        rows = [row for row in (self._table or []) if row]
        if not rows:
            return
        width = max(len(row) for row in rows)

        def line(cells: list[str]) -> str:
            padded = cells + [""] * (width - len(cells))
            return "| " + " | ".join(padded) + " |"

        self._parts.append(line(rows[0]) + "\n")
        self._parts.append("| " + " | ".join("---" for _ in range(width)) + " |\n")
        for row in rows[1:]:
            self._parts.append(line(row) + "\n")

    def text(self) -> str:
        raw = "".join(self._parts).replace("\r\n", "\n").replace("\r", "\n")
        lines = [" ".join(line.split()) for line in raw.split("\n")]
        compact: list[str] = []
        blank = 0
        for line in lines:
            if line:
                blank = 0
                compact.append(line)
            else:
                blank += 1
                if blank <= 1:
                    compact.append("")
        return "\n".join(compact).strip()


def html_to_text(html: str) -> str:
    parser = _HtmlToText()
    parser.feed(html or "")
    parser.close()
    return parser.text()


def load_confluence_settings() -> ConfluenceSettings | None:
    base = os.getenv("CONFLUENCE_BASE_URL", "").strip().rstrip("/")
    token = os.getenv("CONFLUENCE_API_TOKEN", "").strip()
    space = os.getenv("CONFLUENCE_SPACE_KEY", "").strip()
    email = os.getenv("CONFLUENCE_EMAIL", "").strip()
    if not base or not token or not space:
        return None
    try:
        max_pages = int(os.getenv("CONFLUENCE_MAX_PAGES", "25"))
    except ValueError:
        max_pages = 25
    return ConfluenceSettings(
        base_url=base,
        email=email,
        api_token=token,
        space_key=space,
        max_pages=max(1, min(max_pages, 100)),
    )


class ConfluenceClient:
    """Lists pages in one space. Cloud uses basic auth; DC uses a bearer PAT."""

    def __init__(self, settings: ConfluenceSettings) -> None:
        self.settings = settings

    def list_pages(self) -> list[ConfluencePage]:
        pages: list[ConfluencePage] = []
        start = 0
        limit = min(25, self.settings.max_pages)
        while len(pages) < self.settings.max_pages:
            batch, next_start = self._fetch_batch(start=start, limit=limit)
            pages.extend(batch)
            if next_start is None or not batch:
                break
            start = next_start
        return pages[: self.settings.max_pages]

    def _fetch_batch(self, *, start: int, limit: int) -> tuple[list[ConfluencePage], int | None]:
        url = f"{self.settings.base_url}/rest/api/content"
        headers = {"Accept": "application/json"}
        auth: tuple[str, str] | None = None
        if self.settings.email:
            auth = (self.settings.email, self.settings.api_token)
        else:
            headers["Authorization"] = f"Bearer {self.settings.api_token}"
        params = {
            "spaceKey": self.settings.space_key,
            "type": "page",
            "expand": "body.storage,version",
            "limit": str(limit),
            "start": str(start),
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url, headers=headers, params=params, auth=auth)
        except httpx.HTTPError as exc:
            raise AppError(code="API_UNAVAILABLE", status_code=502) from exc
        if response.status_code in {401, 403}:
            raise AppError(code="INVALID_TOKEN", status_code=401)
        if response.status_code >= 400:
            raise AppError(code="API_UNAVAILABLE", status_code=502)
        payload = response.json()
        results = payload.get("results") or []
        pages = [self._to_page(item) for item in results if isinstance(item, dict)]
        size = int(payload.get("size") or len(results))
        next_start = start + size if payload.get("_links", {}).get("next") else None
        return pages, next_start

    def _to_page(self, item: dict) -> ConfluencePage:
        page_id = str(item.get("id") or "")
        title = str(item.get("title") or page_id or "page")
        version = int((item.get("version") or {}).get("number") or 1)
        html = str(((item.get("body") or {}).get("storage") or {}).get("value") or "")
        webui = str((item.get("_links") or {}).get("webui") or "")
        if webui:
            origin = self.settings.base_url.split("/wiki")[0]
            url = urljoin(origin + "/", webui.lstrip("/"))
        else:
            url = f"{self.settings.base_url}/pages/viewpage.action?pageId={page_id}"
        return ConfluencePage(page_id=page_id, title=title, version=version, html=html, url=url)
