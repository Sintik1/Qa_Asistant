"""Replace prompt markers with the parsed requirements or template text."""

from __future__ import annotations

import re

REQUIREMENTS_PLACEHOLDERS: tuple[str, ...] = (
    "*Тут текст требований*",
    "*Тут вставить текст требований*",
    "*Тут вставить текстовый формат документа*",
    "*Тут вставить документ*",
    "<ТУТ БУДЕТ ВСТАВЛЕН ТЕКСТ ДОКУМЕНТА>",
    "<ТУТ БУДЕТ ВСТАВЛЕН ТЕКСТ ТРЕБОВАНИЙ>",
)

TEMPLATE_PLACEHOLDERS: tuple[str, ...] = (
    "*Тут вставить шаблон*",
    "*Вставить шаблон*",
    "*Тут текст шаблонов*",
    "*Тут вставить шаблоны*",
    "*Тут вставить шаблоны сценариев*",
    "*Тут вставить шаблон сценариев*",
)


def fill_prompt_placeholders(
    prompt: str | None,
    *,
    requirements_text: str | None = None,
    template_text: str | None = None,
) -> str | None:
    """Substitute known markers. A prompt without those markers is returned as-is."""
    if prompt is None:
        return None
    filled = prompt
    requirements = (requirements_text or "").strip()
    template = (template_text or "").strip()
    if requirements:
        filled = _replace_markers(filled, REQUIREMENTS_PLACEHOLDERS, requirements)
    if template:
        filled = _replace_markers(filled, TEMPLATE_PLACEHOLDERS, template)
    return filled


def _replace_markers(text: str, markers: tuple[str, ...], value: str) -> str:
    for marker in markers:
        pattern = re.compile(re.escape(marker), flags=re.IGNORECASE)
        text = pattern.sub(lambda _match, replacement=value: replacement, text)
    return text
