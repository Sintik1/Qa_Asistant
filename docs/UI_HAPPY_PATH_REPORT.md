# UI Happy Path report (Chrome DevTools MCP)

> Сводка цикла: [`FULL_QA_REPORT.md`](FULL_QA_REPORT.md) §5.

Date: 2026-10-03  
Issue: [#29](https://github.com/Sintik1/Qa_Asistant/issues/29)  
FE: `http://127.0.0.1:5173`  
API: `http://127.0.0.1:5001` (`AUTH_DEV_BYPASS=1`; port 5000 occupied by AirTunes)

## Steps

| # | Step | Result |
|---|------|--------|
| 1 | Open Home | PASS |
| 2 | Health + settings fetch | PASS (after CORS `127.0.0.1:5173`) |
| 3 | Upload `login_requirements.md` | PASS → `POST /api/documents/upload` 201 |
| 4 | Task + prompt → Generate | PASS → run 201 + generate 200 |
| 5 | Results table (3 cases) + Download CSV | PASS |
| 6 | Console errors | PASS (none) |
| 7 | Reject `.exe` | PASS — alert TZ: «Поддерживаются только PDF, DOCX, DOC и Markdown-файлы» |

## Network (happy path)

- `GET /api/health` 200
- `GET /api/settings` 200
- `POST /api/documents/upload` 201
- `POST /api/runs` 201
- `POST /api/runs/<id>/generate` 200

## Fixes applied during QA

1. **AirTunes on :5000** — Flask on **5001**; `VITE_API_BASE_URL=http://127.0.0.1:5001`
2. **CORS** — whitelist `http://127.0.0.1:5173` (and 8080)
3. **`AUTH_DEV_BYPASS`** — default local user when JWT / `X-User-Id` absent (FE without Supabase)

## Known non-blocker

Small local model (`qwen2.5:1.5b`) sometimes fills `Step` with JSON-like noise. Functional pipeline OK; quality depends on model.
