# UptimeRobot + health monitoring (CI/CD ДЗ шаг 6)

G8 = **UptimeRobot free**. G2 = **C (CI-only)** — нет публичного Flask URL, пока AI локальный.

## 1. Health endpoint

```http
GET /api/health
```

Публичный (без JWT). HTTP **200**, пока процесс жив.

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

UptimeRobot **HTTP(s)** monitor: URL = `https://<public-host>/api/health`, keyword = `qa-assistant` (или `"status":"ok"` если хочешь алерт на degraded).

## 2. UptimeRobot (когда появится публичный URL)

1. Зарегистрируйся на [UptimeRobot](https://uptimerobot.com/) (free).
2. **Add New Monitor** → type **HTTP(s)**.
3. URL: `https://YOUR_HOST/api/health`
4. Interval: 5 min (free).
5. Alert Contacts: email (и опционально Telegram через webhook).
6. Optional: Keyword Monitoring → `qa-assistant`.

Пока G2=C и API только на `127.0.0.1` — внешний монитор **не видит** localhost. Варианты:
- временно публичный туннель (ngrok / Cloudflare Tunnel) только для health;
- или ждать деплоя Flask (G2 A/B).

## 3. Локальный watcher (сейчас)

```bash
# один ping
python scripts/watch_health.py

# каждые 30с, бесконечно
INTERVAL_SEC=30 WATCH_LOOPS=0 python scripts/watch_health.py
```

Env: `HEALTH_URL` (default `http://127.0.0.1:5001/api/health`).

## 4. Код

| Файл | Роль |
|------|------|
| `core/health.py` | checks payload |
| `app/routes.py` | `GET /api/health` |
| `scripts/watch_health.py` | local monitor |
| `tests/test_health_monitoring.py` | contract |
