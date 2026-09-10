---
name: qa-assistant-backend
description: >-
  Flask backend conventions for QA Assistant (layered/Clean Architecture,
  core engines, Leopold/AI integration, thin HTTP layer). Use when creating or
  changing Python API, document parsing, chunking, test-case generation, CSV
  export, or integrations under the backend tree.
---

# QA Assistant Backend

## Stack

- Python 3.11+ / 3.14+ (per TZ), Flask 3.x, Pytest, Docker
- AI: Leopold API (`Qwen/Qwen2.5-72B-Instruct`) via `integrations/`
- Secrets: `.env` only (`QA_ASISTANT_API_URL`, token, chunk settings)

## Target layout (when backend is added)

Prefer the structure from `.cursorrules` next to `qa-assistant/`:

- `app.py` or `app/` — thin HTTP endpoints only
- `core/` — business logic without Flask (`doc_reader`, `parse_engine`, `table_engine`, `csv_writer`, `prompt_builder`)
- `integrations/` — Leopold client and external APIs
- `data/` — JSON stores (prompts, templates, learning data)
- `uploads/` — runtime files (`pending/`, `debug/<uuid>/`); gitignored
- `tests/`, `tools/`, `scripts/`, `docs/`

## Layer rules

1. **HTTP (API)** — parse request, call use case/service, return DTO/JSON. No business rules.
2. **Application** — orchestration (extract → chunk → AI → validate → CSV).
3. **Domain/core** — pure rules; no Flask, no raw SQLAlchemy session usage.
4. **Infrastructure** — DB/files/HTTP clients behind interfaces (Repository / clients).

## DI

- Wire DB sessions, repositories, and clients at composition root (app factory), not inside `core/`.
- Do not instantiate Leopold clients or open DB connections inside domain functions.

## Document pipeline (TZ)

1. Validate upload: PDF/DOCX/DOC/MD, max 100 MB
2. Extract text (structure preserved); DOC → convert first
3. Chunk (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `CHUNK_METHOD` from env)
4. Call AI with `DEFAULT_SYSTEM_PROMPT` / `CHUNK_SYSTEM_PROMPT`
5. Validate → CSV columns: `Name`, `Status=Approved`, `Step`, `Expected Result` (UTF-8 BOM)
6. Save debug artifacts under `uploads/debug/<uuid>/`

## Errors

Return TZ user-facing messages (same strings as frontend `ERROR_MESSAGES`). Never leak stack traces or tokens to the client.

## Do not

- Store secrets in code
- Put `commit()`/`rollback()` in random layers (use Unit of Work — see `qa-assistant-data`)
- Invent endpoints/features outside TZ without asking
