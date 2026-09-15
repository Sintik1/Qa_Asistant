---
name: qa-assistant-testing
description: >-
  Testing conventions for QA Assistant: Pytest for backend (unit + API),
  frontend checks, golden CSV fixtures. Use when adding features, fixing bugs,
  or writing tests under tests/ or qa-assistant/.
---

# QA Assistant Testing

## Backend (Pytest)

Required for new business logic:

| Layer | Test type |
|-------|-----------|
| `core/` domain/application | unit tests |
| HTTP API | integration / contract tests |
| Leopold client | mock HTTP; no real token in CI |
| CSV output | golden fixtures (`tests/fixtures/`) |

Suggested files (from project conventions):

- `tests/test_api_smoke.py`
- `tests/test_api_error_contract.py` — TZ error strings
- `tests/test_csv_parser_golden.py`

## Frontend

- Prefer testing pure utils first: `fileValidation`, `buildCsvFileName`, `formatFileSize`.
- Component tests: Vitest + Testing Library (`*.test.tsx`, jsdom via `environmentMatchGlobs`).
- Cover TZ wiring in UI (`ErrorMessage`, `GenerationAlerts`, `role=alert`) and basic controls (`Button`, `ProgressBar`).
- Manual check: `npm run build` must pass after UI changes.

## Quality gates before done

Backend: Pytest (+ Ruff/Mypy when configured).  
Frontend: `npm run build` (and lint if configured).

## Fixtures

- Keep sample docs/CSV under `tests/fixtures/`.
- Do not commit real customer documents or API tokens.
- Prefer deterministic chunking/AI mocks over live Leopold calls in CI.

## Contract tests

Assert API error messages equal TZ strings (same as frontend `ERROR_MESSAGES`).
