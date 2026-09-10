---
name: qa-assistant-api
description: >-
  Frontend↔backend API contract for QA Assistant (upload, generate, export,
  settings/token, error payload shape). Use when adding or changing HTTP
  endpoints, fetch/axios clients in React, or aligning TZ error messages.
---

# QA Assistant API Contract

## Principles

- Thin Flask routes; typed request/response DTOs (Pydantic or explicit schemas).
- React talks only to HTTP API — no direct FS/DB access from the browser.
- Base URL: `VITE_API_BASE_URL` (see `qa-assistant/.env.example`).

## MVP endpoints (target)

Align names when implementing; do not invent extras without asking.

| Concern | Behavior |
|---------|----------|
| Upload document | Accept PDF/DOCX/DOC/MD ≤ 100 MB; return file meta or job id |
| Generate | Start extraction → chunk → AI → CSV; progress messaging |
| Download CSV | `test_cases_YYYYMMDD_HHMMSS.csv` or Figma-style `Тест кейсы_<name>.csv` |
| Settings / token | Configure API token; never echo full token back |
| Health / config check | Optional diagnostics (see TZ tools) |

## Error payload (recommended)

```json
{
  "error": {
    "code": "INVALID_FORMAT",
    "message": "Поддерживаются только PDF, DOCX, DOC и Markdown-файлы"
  }
}
```

`message` **must** match TZ / `qa-assistant/src/utils/constants.ts` `ERROR_MESSAGES`.

## Frontend client rules

- Centralize fetch in `src/` api helper (create when wiring backend).
- Disable generate until requirements file is valid.
- Show `ProgressBar` labels: «Извлечение текста.» / «Генерация тест-кейсов...»
- On missing/invalid token → navigate/link to `/settings`.

## Security

- No API tokens in frontend source or git.
- Reject dangerous extensions (`.exe`, `.bat`, …) on server.
- Limit body size consistently with 100 MB rule.

## Do not

- Change error wording without updating both backend and frontend constants.
- Expose debug raw AI responses to all users without TZ flows (admin/save raw).
