# DB persistence test report (signup + happy path)

> Сводка цикла: [`FULL_QA_REPORT.md`](FULL_QA_REPORT.md) §6.

Date: 2026-10-03  
Issue: [#31](https://github.com/Sintik1/Qa_Asistant/issues/31)

## Gap found

Flask API previously used **in-memory** repositories only → Supabase tables stayed at **0 rows** after UI/API flows.

## Fix

- `infrastructure/supabase_rest.py` + `infrastructure/supabase_store.py` (PostgREST + RLS via user JWT)
- `create_app` selects Supabase when `PERSIST_BACKEND=auto|supabase` and `SUPABASE_URL` + anon/service present
- Domain ↔ DB status mapping: `extracted↔parsed`, `completed↔done`, `generating↔calling_ai`
- Live runner: `scripts/live_db_happy_path.py`
- Health: `GET /api/health` → `"persist": "supabase"|"memory"`

## Registration

| Check | Result |
|-------|--------|
| `auth.users` created on signup | PASS |
| Trigger → `profiles` + `user_settings` | PASS |
| Email confirm required in project | YES (blocked login until `email_confirmed_at` set) |

## Happy path → DB

User: `020b6667-6095-41a9-8d31-586da8a59a17`

| Table | Result |
|-------|--------|
| `profiles` | PASS |
| `user_settings` | PASS |
| `documents` (`parsed` after extract) | PASS (`6c0aed10-…`) |
| `generation_runs` (`done`, case_count) | PASS (`775ad7b2-…`) |
| `test_cases` (≥1 rows) | PASS (2) |

API: upload 201 → run 201 → generate 200 (2 cases).  
PostgREST RLS readback as same JWT: all PASS.

## Pytest

Mapping + API suite (memory path unchanged): green after wiring (`PERSIST_BACKEND=memory` in auth unit tests).

## Autonomous re-test (agent, no user clicks)

Date: 2026-10-03 (same day, follow-up)

| Step | How | Result |
|------|-----|--------|
| Create confirmed user | Supabase MCP SQL → `auth.users` + `identities` | PASS (`qa.auto.f1197f749e@qatest.local`) |
| Trigger profile/settings | SQL verify | PASS |
| API happy path | login → upload → generate (retry once on API_EMPTY) | PASS |
| UI login | Chrome DevTools `/auth` → Home + email in nav | PASS |
| UI generate | upload md → generate → «Генерация завершена» (8 cases) | PASS |
| Network | Auth token 200; upload 201; run 201; generate 200 | PASS |
| DB after UI+API | documents ≥2 (`persist_reqs.md`, `ui_auto_reqs.md`), runs/cases >0 | PASS |

Public Auth signup hit **email rate limit (429)**; autonomous path uses SQL-seeded confirmed user (same RLS/JWT integration).

## Notes for local demo

1. Prefer `PERSIST_BACKEND=auto` with `SUPABASE_URL` + `SUPABASE_ANON_KEY`.
2. For signup without mailbox: disable **Confirm email** in Supabase Auth, or set `SUPABASE_SERVICE_ROLE_KEY` (admin confirm), or confirm/create via SQL (agent does this).
3. Optional: `SUPABASE_SERVICE_ROLE_KEY` also enables Supabase Storage for document blobs (else local `uploads/`).
