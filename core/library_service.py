"""CRUD for a user's named prompts or scenario templates."""

from __future__ import annotations

from core.errors import NotFoundError, ValidationError
from core.models import LibraryItem
from core.repositories import LibraryRepository

NAME_MAX = 200
CONTENT_MAX = 20_000


class LibraryService:
    def __init__(self, repository: LibraryRepository, *, kind_label: str) -> None:
        self._repository = repository
        self._kind_label = kind_label

    def list_for_user(self, user_id: str) -> list[LibraryItem]:
        return self._repository.list_for_user(user_id)

    def create(self, user_id: str, name: str, content: str) -> LibraryItem:
        clean_name, clean_content = _require_fields(name, content)
        self._ensure_unique_name(user_id, clean_name, except_id=None)
        return self._repository.create(user_id, clean_name, clean_content)

    def update(
        self,
        item_id: str,
        user_id: str,
        *,
        name: str | None = None,
        content: str | None = None,
    ) -> LibraryItem:
        if name is None and content is None:
            raise ValidationError(code="VALIDATION_ERROR", message="Нет полей для обновления")
        current = self._repository.get(item_id, user_id)
        if current is None:
            raise NotFoundError()
        next_name = current.name if name is None else _clean_name(name)
        next_content = current.content if content is None else _clean_content(content)
        if next_name != current.name:
            self._ensure_unique_name(user_id, next_name, except_id=item_id)
        updated = self._repository.update(
            item_id,
            user_id,
            name=next_name,
            content=next_content,
        )
        if updated is None:
            raise NotFoundError()
        return updated

    def delete(self, item_id: str, user_id: str) -> None:
        if not self._repository.delete(item_id, user_id):
            raise NotFoundError()

    def _ensure_unique_name(self, user_id: str, name: str, *, except_id: str | None) -> None:
        for item in self._repository.list_for_user(user_id):
            if item.name == name and item.id != except_id:
                raise ValidationError(
                    code="VALIDATION_ERROR",
                    message=f"{self._kind_label} с таким именем уже есть",
                )


def _require_fields(name: str, content: str) -> tuple[str, str]:
    return _clean_name(name), _clean_content(content)


def _clean_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        raise ValidationError(code="VALIDATION_ERROR", message="Укажите имя")
    if len(cleaned) > NAME_MAX:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message=f"Имя длиннее {NAME_MAX} символов",
        )
    return cleaned


def _clean_content(content: str) -> str:
    cleaned = (content or "").strip()
    if not cleaned:
        raise ValidationError(code="VALIDATION_ERROR", message="Укажите текст")
    if len(cleaned) > CONTENT_MAX:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message=f"Текст длиннее {CONTENT_MAX} символов",
        )
    return cleaned
