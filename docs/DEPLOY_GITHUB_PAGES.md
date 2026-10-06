# Deploy Frontend → GitHub Pages (acceptance: auto-deploy)

Public UI: **https://sintik1.github.io/Qa_Asistant/**

Pipeline: `.github/workflows/ci.yml` job **Deploy frontend (GitHub Pages)** runs on every push to `main` after green frontend+backend checks.

## One-time setup (repo Settings)

1. GitHub → **Settings → Pages**
2. **Source:** GitHub Actions (not “Deploy from a branch”)
3. Optional Repository **Variables** (Settings → Secrets and variables → Actions → Variables):
   - `VITE_SUPABASE_URL` — so Auth works on Pages
   - `VITE_SUPABASE_ANON_KEY` — publishable anon key
   - `VITE_YANDEX_METRIKA_ID` — default build uses `113444012` if unset
   - `VITE_API_BASE_URL` — only if you expose a public Flask URL

## What is deployed

| Layer | Where |
|-------|--------|
| React UI | GitHub Pages (auto) |
| Flask + Ollama | Local (full generate/RAG) |
| Supabase | Cloud Free |
| Static monitor target | `https://sintik1.github.io/Qa_Asistant/status.json` |

## UptimeRobot

Monitor **HTTPS** keyword on:

`https://sintik1.github.io/Qa_Asistant/status.json`

Keyword: `"status":"ok"` or `qa-assistant`.

Local Flask health remains: `GET http://127.0.0.1:5001/api/health` (+ `scripts/watch_health.py`).

## Local build with Pages base (smoke)

```bash
cd qa-assistant
VITE_BASE_PATH=/Qa_Asistant/ npm run build
npx vite preview --base /Qa_Asistant/
```
