"""Document binary + extracted-text persistence (Supabase Storage or local disk)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import quote

import httpx


class DocumentStorage(Protocol):
    def save(
        self,
        *,
        user_id: str,
        document_id: str,
        filename: str,
        data: bytes,
        content_type: str | None,
        extracted_text: str,
    ) -> str:
        """Persist file (+ text sidecar). Return storage_path."""

    def read_extracted_text(self, storage_path: str) -> str | None: ...


@dataclass
class LocalDocumentStorage:
    """Fallback for pytest / when Supabase keys are absent. Root is gitignored uploads/."""

    root: Path

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, user_id: str, document_id: str) -> Path:
        path = self.root / user_id / document_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(
        self,
        *,
        user_id: str,
        document_id: str,
        filename: str,
        data: bytes,
        content_type: str | None,
        extracted_text: str,
    ) -> str:
        folder = self._dir(user_id, document_id)
        safe_name = Path(filename).name or "document.bin"
        (folder / safe_name).write_bytes(data)
        (folder / "extracted.txt").write_text(extracted_text, encoding="utf-8")
        return f"documents/{user_id}/{document_id}/{safe_name}"

    def read_extracted_text(self, storage_path: str) -> str | None:
        # documents/{user}/{doc_id}/{filename}
        parts = storage_path.strip("/").split("/")
        if len(parts) < 4 or parts[0] != "documents":
            return None
        user_id, document_id = parts[1], parts[2]
        text_path = self.root / user_id / document_id / "extracted.txt"
        if not text_path.is_file():
            return None
        return text_path.read_text(encoding="utf-8")


@dataclass
class SupabaseDocumentStorage:
    """Upload to private bucket `documents` via Storage REST (service role)."""

    base_url: str
    service_role_key: str
    bucket: str = "documents"
    local_fallback: LocalDocumentStorage | None = None

    def save(
        self,
        *,
        user_id: str,
        document_id: str,
        filename: str,
        data: bytes,
        content_type: str | None,
        extracted_text: str,
    ) -> str:
        safe_name = Path(filename).name or "document.bin"
        object_path = f"{user_id}/{document_id}/{safe_name}"
        text_path = f"{user_id}/{document_id}/extracted.txt"

        self._put_object(object_path, data, content_type or "application/octet-stream")
        self._put_object(text_path, extracted_text.encode("utf-8"), "text/plain; charset=utf-8")

        # Keep local copy for generate fallback without round-trip in same process.
        if self.local_fallback is not None:
            self.local_fallback.save(
                user_id=user_id,
                document_id=document_id,
                filename=safe_name,
                data=data,
                content_type=content_type,
                extracted_text=extracted_text,
            )
        return f"documents/{object_path}"

    def read_extracted_text(self, storage_path: str) -> str | None:
        if self.local_fallback is not None:
            local = self.local_fallback.read_extracted_text(storage_path)
            if local is not None:
                return local
        parts = storage_path.strip("/").split("/")
        if len(parts) < 4 or parts[0] != "documents":
            return None
        user_id, document_id = parts[1], parts[2]
        object_path = f"{user_id}/{document_id}/extracted.txt"
        url = f"{self.base_url.rstrip('/')}/storage/v1/object/{self.bucket}/{quote(object_path, safe='/')}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url, headers=headers)
        except httpx.HTTPError:
            return None
        if response.status_code >= 400:
            return None
        return response.text

    def _put_object(self, object_path: str, data: bytes, content_type: str) -> None:
        url = f"{self.base_url.rstrip('/')}/storage/v1/object/{self.bucket}/{quote(object_path, safe='/')}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=headers, content=data)
        if response.status_code >= 400:
            raise RuntimeError(f"Supabase Storage upload failed: {response.status_code} {response.text[:200]}")


def build_document_storage(*, testing: bool = False) -> DocumentStorage:
    root = Path(os.getenv("UPLOADS_DIR", "uploads")) / "documents"
    local = LocalDocumentStorage(root=root)
    if testing:
        return local

    url = (os.getenv("SUPABASE_URL") or "").strip()
    key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key or key.startswith("your_"):
        return local

    return SupabaseDocumentStorage(
        base_url=url,
        service_role_key=key,
        bucket=os.getenv("SUPABASE_DOCUMENTS_BUCKET", "documents"),
        local_fallback=local,
    )
