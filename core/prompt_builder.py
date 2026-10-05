"""Build AI prompts from parsed leaf sections (structure → case / items → steps)."""

from __future__ import annotations

from core.section_parser import LeafSection, ParsedDocument

SECTION_SYSTEM_PROMPT = (
    "Ты QA-инженер. По одному разделу требований сформируй тест-кейсы.\n"
    "Правила:\n"
    "1) Основной кейс: ОДИН тест-кейс на этот раздел/подраздел.\n"
    "2) Нумерованные пункты доработок (1., 2., 3. …) внутри раздела — это отдельные "
    "ШАГИ (Step) одного кейса, а не отдельные кейсы.\n"
    "3) Таблицы, блоки кода и спецсимволы из раздела сохрани в шагах/ожидаемом результате "
    "без выдумывания данных вне раздела.\n"
    "4) Если в блоке «Примеры шаблонов» есть образцы — добавь ДОПОЛНИТЕЛЬНЫЕ кейсы "
    "(позитив/негатив/границы) в том же стиле, строго по смыслу ЭТОГО раздела.\n"
    "5) Ответь ТОЛЬКО CSV без пояснений, с заголовком:\n"
    "Name,Status,Step,Expected Result\n"
    "Status всегда Approved. Несколько шагов в одном Step разделяй переносом строки "
    "внутри кавычек CSV."
)

# Fallback when no numbered sections detected (legacy single-shot).
FLAT_SYSTEM_PROMPT = (
    "Ты QA-инженер. По требованиям сгенерируй тест-кейсы. "
    "Ответь ТОЛЬКО CSV без пояснений, с заголовком:\n"
    "Name,Status,Step,Expected Result\n"
    "Status всегда Approved. Step может содержать несколько строк в кавычках CSV."
)


def build_leaf_user_prompt(
    leaf: LeafSection,
    *,
    task_name: str | None = None,
    extra_prompt: str | None = None,
    template_examples: str | None = None,
) -> str:
    parts: list[str] = [
        f"Раздел (path): {leaf.path}",
        f"Номер: {leaf.number}",
        f"Заголовок: {leaf.title}",
        "",
        "Текст раздела (целиком, включая таблицы/код):",
        leaf.body or "(пусто)",
    ]
    if leaf.items:
        parts.append("")
        parts.append("Пункты доработок → должны стать шагами ОДНОГО основного кейса:")
        for item in leaf.items:
            parts.append(f"  {item.index}. {item.text}")
    else:
        parts.append("")
        parts.append("Нумерованных пунктов не найдено — сформируй шаги основного кейса из содержания раздела.")
    if template_examples and template_examples.strip():
        parts.extend(
            [
                "",
                "Примеры шаблонов (RAG / библиотека) — добавь похожие доп. кейсы к основному:",
                template_examples.strip(),
            ]
        )
    if task_name and task_name.strip():
        parts.extend(["", f"Имя задачи: {task_name.strip()}"])
    if extra_prompt and extra_prompt.strip():
        parts.extend(["", f"Доп. промпт: {extra_prompt.strip()}"])
    return "\n".join(parts)


def build_flat_user_prompt(
    text: str,
    *,
    task_name: str | None = None,
    extra_prompt: str | None = None,
) -> str:
    parts = [f"Требования:\n{text.strip()}"]
    if task_name and task_name.strip():
        parts.append(f"Имя задачи: {task_name.strip()}")
    if extra_prompt and extra_prompt.strip():
        parts.append(f"Доп. промпт: {extra_prompt.strip()}")
    return "\n\n".join(parts)


def iter_generation_prompts(
    parsed: ParsedDocument,
    *,
    task_name: str | None = None,
    extra_prompt: str | None = None,
    template_examples_by_leaf: dict[str, str] | None = None,
    raw_text_fallback: str | None = None,
) -> list[tuple[str, str, str | None]]:
    """
    Return list of (system_prompt, user_prompt, leaf_number|None).

    If no leaves — one flat prompt over raw/preamble text.
    """
    templates = template_examples_by_leaf or {}
    if parsed.leaves:
        out: list[tuple[str, str, str | None]] = []
        for leaf in parsed.leaves:
            user = build_leaf_user_prompt(
                leaf,
                task_name=task_name,
                extra_prompt=extra_prompt,
                template_examples=templates.get(leaf.number),
            )
            out.append((SECTION_SYSTEM_PROMPT, user, leaf.number))
        return out

    text = (raw_text_fallback or parsed.preamble or "").strip()
    return [
        (
            FLAT_SYSTEM_PROMPT,
            build_flat_user_prompt(text, task_name=task_name, extra_prompt=extra_prompt),
            None,
        )
    ]
