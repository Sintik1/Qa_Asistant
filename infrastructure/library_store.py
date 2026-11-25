"""Prompt and scenario-template stores. One class, two tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from core.models import LibraryItem
from infrastructure.supabase_rest import SupabaseRestClient


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryLibraryRepository:
    def __init__(self) -> None:
        self._items: dict[str, LibraryItem] = {}

    def list_for_user(self, user_id: str) -> list[LibraryItem]:
        rows = [item for item in self._items.values() if item.user_id == user_id]
        rows.sort(key=lambda item: item.created_at or "", reverse=True)
        return rows

    def get(self, item_id: str, user_id: str) -> LibraryItem | None:
        item = self._items.get(item_id)
        if item is None or item.user_id != user_id:
            return None
        return item

    def create(self, user_id: str, name: str, content: str) -> LibraryItem:
        stamp = _now()
        item = LibraryItem(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            content=content,
            created_at=stamp,
            updated_at=stamp,
        )
        self._items[item.id] = item
        return item

    def update(
        self,
        item_id: str,
        user_id: str,
        *,
        name: str | None,
        content: str | None,
    ) -> LibraryItem | None:
        item = self.get(item_id, user_id)
        if item is None:
            return None
        if name is not None:
            item.name = name
        if content is not None:
            item.content = content
        item.updated_at = _now()
        return item

    def delete(self, item_id: str, user_id: str) -> bool:
        item = self.get(item_id, user_id)
        if item is None:
            return False
        del self._items[item_id]
        return True


def _item_from_row(row: dict) -> LibraryItem:
    return LibraryItem(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=str(row["name"]),
        content=str(row["content"]),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


class SupabaseLibraryRepository:
    def __init__(self, client: SupabaseRestClient, table: str) -> None:
        self._client = client
        self._table = table

    def list_for_user(self, user_id: str) -> list[LibraryItem]:
        rows = self._client.select(
            self._table,
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
            },
        )
        return [_item_from_row(row) for row in rows]

    def get(self, item_id: str, user_id: str) -> LibraryItem | None:
        rows = self._client.select(
            self._table,
            params={
                "id": f"eq.{item_id}",
                "user_id": f"eq.{user_id}",
                "limit": "1",
            },
        )
        return _item_from_row(rows[0]) if rows else None

    def create(self, user_id: str, name: str, content: str) -> LibraryItem:
        rows = self._client.insert(
            self._table,
            {"user_id": user_id, "name": name, "content": content},
        )
        return _item_from_row(rows[0])

    def update(
        self,
        item_id: str,
        user_id: str,
        *,
        name: str | None,
        content: str | None,
    ) -> LibraryItem | None:
        patch: dict[str, str] = {}
        if name is not None:
            patch["name"] = name
        if content is not None:
            patch["content"] = content
        if not patch:
            return self.get(item_id, user_id)
        rows = self._client.patch(
            self._table,
            params={"id": f"eq.{item_id}", "user_id": f"eq.{user_id}"},
            patch=patch,
        )
        return _item_from_row(rows[0]) if rows else None

    def delete(self, item_id: str, user_id: str) -> bool:
        if self.get(item_id, user_id) is None:
            return False
        self._client.delete(
            self._table,
            params={"id": f"eq.{item_id}", "user_id": f"eq.{user_id}"},
        )
        return True
