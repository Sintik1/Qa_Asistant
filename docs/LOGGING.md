# Logging (CI/CD ДЗ шаг 7)

JSON structured logs + AI analysis scenarios. Centralization at G2=C = local files (+ optional ship later).

## 1. Format

One JSON object per line (`LOG_JSON=1`, default):

| Field | Meaning |
|-------|---------|
| `ts` | UTC ISO timestamp |
| `level` | DEBUG / INFO / WARNING / ERROR |
| `logger` | `qa_assistant` |
| `service` | `LOG_SERVICE` (default `qa-assistant`) |
| `env` | `APP_ENV` / `FLASK_ENV` |
| `event` | `http_request`, `app_error`, `not_found`, … |
| `msg` | message |
| `request_id` | correlates with `X-Request-Id` |
| `method` / `path` / `status` / `error_code` / `duration_ms` | HTTP context |

Destination:

- stdout (always)
- rotating file `logs/app.log` (`LOG_TO_FILE=1`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`)

## 2. Env

```env
LOG_LEVEL=INFO
LOG_JSON=1
LOG_TO_FILE=1
LOG_DIR=logs
LOG_FILE=app.log
LOG_SERVICE=qa-assistant
APP_ENV=development
LOG_ANALYZE_ENABLED=1
LOG_ANALYZE_ADMIN_TOKEN=change-me
```

## 3. AI analysis scenarios

| Scenario | Focus |
|----------|--------|
| `general` | triage top errors |
| `auth` | 401/403 / JWT / OAuth |
| `cors` | CORS / Origin |
| `ai` | Ollama / timeouts / empty |
| `persist` | Supabase / RLS |

CLI:

```bash
python tools/analyze_logs.py --list-scenarios
python tools/analyze_logs.py --scenario auth --file tests/fixtures/logs/auth_401.jsonl
python tools/analyze_logs.py --scenario ai --file tests/fixtures/logs/ai_timeout.jsonl
tail -n 100 logs/app.log | python tools/analyze_logs.py --stdin --scenario general
```

API (admin token required outside tests):

```http
POST /api/admin/analyze-logs
X-Admin-Token: …
{"scenario":"auth","text":"…jsonl…"}
```

Secrets (Bearer JWT, `sb_secret_*`, api keys) are **redacted** before the model sees the text.

## 4. Centralization (G2=C)

No cloud required:

1. Keep `logs/app.log` on the machine running Flask.
2. Optional later: ship with Vector/Promtail/Papertrail when there is a public host — document URL only; do not put SaaS tokens in `VITE_*`.
3. Supabase Dashboard → Logs remains the source for Auth/PostgREST; paste into `--stdin`.

## 5. Fixtures

`tests/fixtures/logs/`:

- `auth_401.jsonl`
- `cors_noise.jsonl`
- `ai_timeout.jsonl`
