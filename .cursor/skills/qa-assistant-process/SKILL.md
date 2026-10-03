---
name: qa-assistant-process
description: >-
  Mandatory delivery process for QA Assistant: GitHub Issues per stage and
  development_report.md updates. ALWAYS apply at the start/end of every project
  stage, milestone, or plan step. Highest priority with .cursorrules §10–11.
---

# QA Assistant Process (`.cursorrules` §10–12) — ALWAYS

## Non-negotiable

- Нельзя пропускать Issues или `development_report.md`.
- На шагах backend ДЗ дополнительно обновлять `backend_documentation.md`; это **не замена** полного `development_report.md`.
- Нельзя откладывать «на конец недели» или заменять только текстом в чате.
- Стадия без Issue + обновления отчёта = **не завершена**.
- Остальные правила `.cursorrules` (архитектура, тесты, секреты, scope ТЗ/Figma) действуют **без ослабления** на backend ДЗ.

## Required on every stage

1. **GitHub Issue** в `Sintik1/Qa_Asistant` (цель, результат, блокеры, коммиты).
2. **Backend ДЗ (шаги 1–9):** обновить **`backend_documentation.md`** (архитектура, деплой, API, примеры, AI-процесс, журнал §6). Правило: `.cursor/rules/backend-homework-dz.mdc`.
3. Обновить корневой **`development_report.md`**:
   - описание процесса разработки
   - применённые техники работы с AI
   - примеры промптов и результатов
   - проблемы и решения
   - выводы и рекомендации
   - журнал стадий со ссылками на Issues
4. Закрывать Issue только после согласования пользователя, если план требует gate.
5. Правила Cursor: `.cursor/rules/process-tracking.mdc`, `.cursor/rules/backend-homework-dz.mdc` (`alwaysApply: true`).

## Issue hygiene

- One issue per stage/milestone (`Stage N: …`).
- Comment with commit SHA / PR link when code lands.
- Keep the journal table in `development_report.md` in sync.

## Scope discipline

- Ask when business logic, security, migrations, or API contracts are ambiguous.
- Do not invent features outside TZ + Figma.
- Prefer small commits with clear why-focused messages.
