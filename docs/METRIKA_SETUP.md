# Yandex Metrika setup (CI/CD ДЗ шаг 4)

Counter **id is public** (embedded in the frontend bundle). Do not put OAuth tokens or Metrika API tokens in `VITE_*`.

## 1. Create a counter

1. Open [Yandex Metrika](https://metrika.yandex.ru/).
2. Add a counter for your app (local `http://127.0.0.1:5173` or production host).
3. Copy the numeric **counter id**.

**Project counter (ДЗ):** `113444012`

## 2. Configure the SPA

In `qa-assistant/.env.local` (or copy from `.env.example`):

```env
VITE_YANDEX_METRIKA_ID=113444012
```

Restart Vite (`npm run dev`). Empty / missing id → analytics is a no-op (safe for CI).

## 3. Goals to create in Metrika UI

Create goals of type **JavaScript event** with these identifiers (must match `reachGoal` names):

| Goal id | When |
|---------|------|
| `auth_login` | Successful password or OAuth login |
| `auth_signup` | Successful signup |
| `auth_oauth_start` | User clicks Google/Yandex OAuth |
| `document_upload` | Requirements file selected |
| `generate_start` | Generation pipeline starts |
| `generate_success` | Cases generated |
| `generate_error` | Generation failed |
| `csv_download` | CSV export |
| `chat_send` | RAG chat message sent |

SPA pageviews use `ym(id, 'hit', path)` on every React Router change (`MetrikaRouteTracker`).

## 4. Code map

| File | Role |
|------|------|
| `src/analytics/metrika.ts` | init / hit / reachGoal |
| `src/analytics/MetrikaRouteTracker.tsx` | SPA hits |
| Auth / Home / generation / Chat | goals |

## 5. Verify

1. DevTools → Network: requests to `mc.yandex.ru` / `watch/113444012`.
2. Metrika → Real-time (online) after login / generate / CSV.
3. Vitest: `npm test -- src/analytics/metrika.test.ts` (no network).

### 5.1. Live verification (2026-10-05)

Counter **`113444012`**, local Vite + Flask.

| Check | Result |
|-------|--------|
| Vitest `metrika.test.ts` | **4/4 PASS** |
| `tag.js` loaded | **PASS** (`mc.yandex.ru/metrika/tag.js`) |
| `ym(…, 'init')` with id `113444012` | **PASS** |
| SPA `hit` on `/auth`, `/` | **PASS** (`watch/113444012` in Network) |
| Goal `auth_login` after demo password login | **PASS** |
| Goals via `reachGoal` (upload/generate/csv/chat/…) | **PASS** (ym + watch requests) |
| Metrika JS goals in UI | create once in Metrika → Goals (JS event ids from §3) |

Note: full generate→CSV path may still need working Flask JWT (`SUPABASE_JWT_SECRET` or Auth API reachability). Analytics itself does **not** depend on that — counter + hits + goals are verified independently.
