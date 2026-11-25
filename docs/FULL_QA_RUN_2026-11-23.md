# Full QA run — 2026-11-23

Issue: [#45](https://github.com/Sintik1/Qa_Asistant/issues/45)

Hermetic CI-equivalent suite + live Flask/Supabase probes. Selenium UI not executed (no `webdriver_manager`). Ollama not running.

## Summary

| Layer | Result |
|-------|--------|
| Pytest (`not ui`, not security) | **124 passed** |
| Ruff lint | **pass** |
| Ruff format | **pass** after format `core/rag_service.py` |
| Vitest | **92 passed** (20 files) |
| oxlint | **warnings only** (set-state-in-effect ×4, AuthContext export) |
| `npm run build` | **pass** |
| npm audit | **not finished** (registry hang; killed) |
| pip-audit `requirements.txt` | **4 vulns** in 3 packages: `python-dotenv` PYSEC-2026-2270 (≥1.2.2); `anyio` PYSEC-2026-4024/4025 (≥4.14.2); `pytest` PYSEC-2026-1845 (≥9.0.3) |
| Flask `GET /api/health` | **pass** (`persist=supabase`, `rag.enabled=true`, hash embeddings, `ai.configured=true`) |
| Live negatives (401 / INVALID_FORMAT / FILE_TOO_LARGE) | **pass** |
| Live `GET /api/auth/oauth/status` | **pass** |
| Live CRUD/chat via `AUTH_DEV_BYPASS` + PostgREST | **FAIL 403** — REST HTTP 401 (bypass UUID is not a user JWT / RLS) |
| `POST /api/ai/ping` | **FAIL 502** — Ollama down (`:11434` refused) |
| `scripts/live_api_full_qa.py` | **aborted** after AI 502; next POST `/api/documents` timed out 30s → 503 |
| `scripts/supabase_keepalive.py` | **pass** HTTP 200 (project DNS/REST up) |
| Selenium E2E | **ERROR** — `ModuleNotFoundError: webdriver_manager` |

## Reproduce hermetic

```bash
.venv/bin/python -m pytest tests/ -m "not ui and not security" \
  --ignore=tests/test_ui_e2e.py --ignore=tests/test_security.py -q
.venv/bin/ruff check app core infrastructure integrations wsgi.py
.venv/bin/ruff format --check app core infrastructure integrations wsgi.py
cd qa-assistant && npm run lint && npm test && npm run build
```

## Live blockers (not product regressions in unit tests)

1. **Ollama not started** — generate / `/api/ai/ping` 502.
2. **AUTH_DEV_BYPASS + persist=supabase** — PostgREST RLS expects a real JWT; bypass user id → 401 mapped to 403 FORBIDDEN.
3. **Happy-path UI login** needs Vite + resumed project + (if Clash) DIRECT `supabase.co`.
4. **Selenium** needs `webdriver_manager` in the venv (CI excludes these tests).

## Notes

- oxlint warnings pre-existed (Settings/Auth/generation hooks); CI `npm run lint` does not fail the job on these unless configured as errors.
- Format drift in `core/rag_service.py` would have failed GitHub Actions `ruff format --check`; file was reformatted in this run.
