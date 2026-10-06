# UptimeRobot + health monitoring (CI/CD ДЗ шаг 6)

G8 = **UptimeRobot free**. G2 = **B** — Frontend на GitHub Pages (auto-deploy); Flask/AI локально.

## 1. Health endpoint (Flask)

```http
GET /api/health
```

Публичный (без JWT). HTTP **200**, пока процесс жив. Всегда включает блок `checks`.

Пример ответа:

```json
{
  "status": "ok",
  "api": "qa-assistant",
  "mode": "hybrid-c",
  "persist": "supabase",
  "ai": { "provider": "ollama", "configured": true, "model": "qwen2.5:1.5b" },
  "rag": { "enabled": true },
  "checks": {
    "app": { "ok": true },
    "disk": { "ok": true, "path": "uploads", "free_mb": 12000 },
    "db": { "ok": true, "mode": "supabase", "ping": "ok" },
    "ai": { "ok": true, "configured": true, "provider": "ollama" }
  }
}
```

| `status` | Смысл |
|----------|--------|
| `ok` | app + disk + db ok |
| `degraded` | процесс жив, но soft-check (часто DB) failed |
| `fail` | критично (disk) |

## 2. Публичный монитор (GitHub Pages)

После CI deploy UI доступен:

| URL | Назначение |
|-----|------------|
| https://sintik1.github.io/Qa_Asistant/ | Frontend |
| https://sintik1.github.io/Qa_Asistant/status.json | Keyword target для UptimeRobot |

### UptimeRobot — настроить сейчас

1. [UptimeRobot](https://uptimerobot.com/) → **Add New Monitor**
2. Type: **HTTP(s)** (или Keyword)
3. URL: `https://sintik1.github.io/Qa_Asistant/status.json`
4. Keyword (optional): `qa-assistant` или `"status":"ok"`
5. Interval: 5 min

Это закрывает критерий «мониторинг приложения» на публичном URL.  
Flask `/api/health` — локально / туннель / будущий PaaS (см. §3–4).

## 3. Локальный watcher (Flask)

```bash
python scripts/watch_health.py
INTERVAL_SEC=30 WATCH_LOOPS=0 python scripts/watch_health.py
```

Env: `HEALTH_URL` (default `http://127.0.0.1:5001/api/health`).

Перезапусти Flask после обновления кода, чтобы в ответе был блок `checks`.

## 4. Опционально: публичный Flask health

Туннель (ngrok / Cloudflare Tunnel) на `:5001` → второй монитор UptimeRobot на `/api/health`.

## 5. Код

| Файл | Роль |
|------|------|
| `core/health.py` | checks payload |
| `app/routes.py` | `GET /api/health` |
| `qa-assistant/public/status.json` | Pages monitor target |
| `scripts/watch_health.py` | local monitor |
| `tests/test_health_monitoring.py` | contract |
| [`docs/DEPLOY_GITHUB_PAGES.md`](DEPLOY_GITHUB_PAGES.md) | auto-deploy |
