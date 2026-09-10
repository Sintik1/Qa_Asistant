---
name: qa-assistant-process
description: >-
  Mandatory delivery process for QA Assistant: GitHub Issues per stage and
  development_report.md updates. Use at the start/end of every project stage,
  milestone, or when closing a plan step.
---

# QA Assistant Process (`.cursorrules` §10–11)

## Required on every stage

1. **GitHub Issue** in `Sintik1/Qa_Asistant` describing the stage (goal, result, blockers).
2. Update root **`development_report.md`** with:
   - описание процесса разработки
   - применённые техники работы с AI
   - примеры промптов и результатов
   - проблемы и решения
   - выводы и рекомендации
3. Close the issue only after user approval when the plan requires a gate.

## Issue hygiene

- One issue per stage/milestone (`Stage N: …`).
- Comment with commit SHA / PR link when code lands.
- Keep the journal table in `development_report.md` in sync with issue numbers.

## Scope discipline

- Ask when business logic, security, migrations, or API contracts are ambiguous.
- Do not invent features outside TZ + Figma.
- Prefer small commits with clear why-focused messages.
