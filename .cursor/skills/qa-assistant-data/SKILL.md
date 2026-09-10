---
name: qa-assistant-data
description: >-
  Data access rules for QA Assistant: Repository, Unit of Work, SQL safety,
  JSON file stores, uploads/debug persistence. Use when adding models, queries,
  migrations, repositories, transaction boundaries, or reading/writing data/
  and uploads/.
---

# QA Assistant Data Access

## Patterns

### Repository

- All reads/writes go through repository interfaces.
- Business/application code must not import ORM models for querying or build SQL.
- Map ORM ↔ domain entities at the infrastructure boundary.

### Unit of Work

- One UoW per use-case transaction boundary.
- `commit` / `rollback` only inside UoW (or explicit application transaction helper).
- Do not scatter commits across routers, services, and repositories.

### Model separation

Keep separate types:

| Kind | Role |
|------|------|
| ORM model | DB table mapping |
| Domain entity | Business rules |
| DTO / Pydantic schema | API request/response |

Never return ORM objects from HTTP handlers.

## SQL safety

- **Forbidden:** SQL via string concat / f-string with user input.
- **Required:** SQLAlchemy query builder, ORM, or bound parameters.

## File / JSON persistence (current product shape)

- Config/learning data: `data/*.json` (prompts, templates, feedback, contexts).
- Uploads: `uploads/pending/`, `uploads/debug/<run_id>/`.
- `uploads/` must stay in `.gitignore`.
- Treat JSON stores as infrastructure behind a small repository/adapter if logic grows.

## Env-driven data settings

Chunking and API config from `.env` (examples):

- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `CHUNK_METHOD`
- `QA_ASISTANT_API_URL`, API token

Never commit real `.env` values.

## Checklist before merging data changes

- [ ] Repository used (no SQL in domain)
- [ ] UoW owns transaction
- [ ] No secrets in repo
- [ ] `uploads/` ignored
- [ ] Tests for new persistence paths
