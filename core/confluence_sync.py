"""Index one Confluence space into the existing document RAG."""

from __future__ import annotations

import re

from core.models import CreateDocumentCommand, Document
from core.rag_service import RagService
from core.repositories import DocumentRepository
from integrations.confluence_client import ConfluenceClient, html_to_text

_FILENAME_SAFE = re.compile(r"[^\w.\- ()]+", re.UNICODE)


def page_storage_key(space: str, page_id: str, version: int) -> str:
    """Include the embedding model so a model change reindexes the same page version."""
    import os

    model = (os.getenv("EMBEDDING_MODEL") or "").strip()
    suffix = "page" if not model or model in {"hash", "hash-v1"} else re.sub(r"[^A-Za-z0-9._-]+", "-", model)[:40]
    # Format token forces a resync when the stored Markdown changes shape.
    return f"confluence/{space}/{page_id}@v{version}+{suffix}-blocks"


def _filename(title: str) -> str:
    cleaned = _FILENAME_SAFE.sub(" ", title).strip() or "page"
    cleaned = re.sub(r"\s+", " ", cleaned)[:100]
    return f"{cleaned}.md"


class ConfluenceSyncService:
    def __init__(self, docs: DocumentRepository, rag: RagService, client: ConfluenceClient) -> None:
        self._docs = docs
        self._rag = rag
        self._client = client

    def sync_space(self, user_id: str) -> dict[str, int | str]:
        space = self._client.settings.space_key
        pages = self._client.list_pages()
        existing = self._docs.list_for_user(user_id)
        indexed = 0
        skipped = 0
        for page in pages:
            body = html_to_text(page.html)
            text = f"# {page.title}\n\n{body}".strip()
            if len(text) < 8:
                skipped += 1
                continue
            storage_path = page_storage_key(space, page.page_id, page.version)
            doc = _find_page(existing, space, page.page_id)
            if doc is not None and doc.storage_path == storage_path and doc.status == "extracted":
                skipped += 1
                continue
            if doc is None:
                doc = self._docs.create(
                    CreateDocumentCommand(
                        user_id=user_id,
                        original_filename=_filename(page.title),
                        size_bytes=len(text.encode("utf-8")),
                        mime_type="text/html",
                        storage_path=storage_path,
                    )
                )
                existing.append(doc)
            else:
                doc.original_filename = _filename(page.title)
                doc.size_bytes = len(text.encode("utf-8"))
                doc.storage_path = storage_path
            self._rag.index_document_text(
                user_id=user_id,
                document_id=doc.id,
                text=text,
                as_single_chunk=True,
                extra_metadata={
                    "source": "confluence",
                    "space_key": space,
                    "page_id": page.page_id,
                    "version": page.version,
                    "url": page.url,
                },
            )
            doc.status = "extracted"
            self._docs.save(doc)
            indexed += 1
        return {
            "space": space,
            "pages": len(pages),
            "indexed": indexed,
            "skipped": skipped,
        }


def _find_page(docs: list[Document], space: str, page_id: str) -> Document | None:
    prefix = f"confluence/{space}/{page_id}@"
    for doc in docs:
        if doc.storage_path.startswith(prefix):
            return doc
    return None
