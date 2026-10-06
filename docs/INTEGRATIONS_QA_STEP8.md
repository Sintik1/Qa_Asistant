# Integrations QA + optimization — CI/CD ДЗ шаг 8

Tracked: [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
Date: 2026-10-06

## 1. Scope (gates)

| Integration | Gate | How tested |
|-------------|------|------------|
| OAuth2 Google + Yandex | G5=C | Pytest `test_oauth.py` + live `/status` + UI start redirects |
| Яндекс.Метрика | G6=A | Vitest `metrika.test.ts` + live `tag.js` + `watch/113444012` |
| Платежи | G7 skip | **N/A** — not integrated |
| CI/CD | G1=A, G2=C | Local CI parity (ruff / pytest / vitest / build / audits already in workflow); Actions API from agent env = Forbidden |

## 2. Results matrix

| Check | Result | Evidence |
|-------|--------|----------|
| Pytest OAuth | **PASS** | `tests/test_oauth.py` (part of 114) |
| Live `GET /api/auth/oauth/status` | **PASS** | google+yandex `env_client_configured` + `service_role_ready` |
| Live Google `/start` → provider | **FAIL (config)** | `redirect_uri_mismatch` — URI `http://127.0.0.1:5001/api/auth/oauth/google/callback` not registered in Google Cloud Console (code OK; see `docs/OAUTH_SETUP.md` §4.1) |
| Live Yandex `/start` → provider | **PASS** | Redirect to `passport.yandex.ru` / `oauth.yandex.ru` with correct `redirect_uri` |
| Vitest Metrika | **PASS** | 85 FE tests incl. `metrika.test.ts` |
| Live Metrika tag + SPA hit | **PASS** | `mc.yandex.ru/metrika/tag.js`, `watch/113444012` for `/auth` and `/` |
| Payments | **N/A** | G7 |
| Backend pytest (CI subset) | **PASS** | **114 passed** after fixes |
| FE build | **PASS** | code-split; no 500kB warning |
| Ruff | **PASS** | check + format |
| GitHub Actions list via API | **blocked** | `403 Forbidden` from this environment; workflow file reviewed + local parity run |

## 3. Bugs found → fixed

| # | Bug | Fix |
|---|-----|-----|
| B1 | `bypass_client` with `testing=False` hit real Supabase via proxy → 500 / flaky pytest | `PERSIST_BACKEND=memory` in fixture |
| B2 | Health disk check used `UPLOAD_DIR` but app uses `UPLOADS_DIR` | Prefer `UPLOADS_DIR` in `core/health.py` |
| B3 | PostgREST transport/proxy errors → unhandled 500 | `SupabaseRestClient._send` → `AppError API_UNAVAILABLE` 503 |
| B4 | Vite main chunk >500 kB warning | Route `lazy()` + `manualChunks` (react/router/supabase) |
| B5 | `AuthCallbackPage` sync `setState` in effect for query oauth error | Derive initial error from query |
| B6 | Google live OAuth `redirect_uri_mismatch` | **Config** — document §4.1; must add URI in Google Console (cannot fix in code) |

## 4. AI performance recommendations (applied)

1. Hermetic tests for non-`TESTING` bypass paths (memory persist).
2. Map infrastructure HTTP failures to TZ error codes (no raw 500).
3. Align env names (`UPLOADS_DIR`) across health and storage.
4. Route-level code splitting + vendor chunks for faster TTI.
5. Avoid unnecessary render cascades on OAuth callback error path.

## 5. Residual / ops notes

- Running Flask process on `:5001` may be an older build without `checks` in `/api/health` until restart; code + pytest health contract are current.
- Google OAuth end-to-end login blocked until Console redirect URI is fixed (B6).
- Full payment flows not in product scope.
