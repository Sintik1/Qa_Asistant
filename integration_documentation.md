# Integration Documentation — QA Assistant

**Файл сдачи ДЗ:** `integration_documentation.md`  
**Репозиторий:** https://github.com/Sintik1/Qa_Asistant  
**Эпик:** [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
**Живой журнал работ:** [`cicd_integrations_documentation.md`](cicd_integrations_documentation.md)

Документ соответствует формату сдачи: CI/CD · интеграции сервисов · security · мониторинг · логирование · примеры конфигураций.

---

## 0. Соответствие формату сдачи (чеклист)

| # | Требование формата | Статус | Где в репо |
|---|-------------------|--------|------------|
| **1** | Репозиторий GitHub | ✅ | https://github.com/Sintik1/Qa_Asistant |
| 1a | Код с интеграциями | ✅ | OAuth (`app/oauth_routes.py`, `integrations/oauth_*`), Metrika (`qa-assistant/src/analytics/`), health/logs |
| 1b | Конфигурация CI/CD | ✅ | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| 1c | Обновлённая документация | ✅ | этот файл + `security_audit.md` + README |
| **2** | Работающее приложение | ✅\* | \*G2=C: **локальный стенд** + screencast (публичный auto-deploy отключён — локальный Ollama) |
| 2a | Приложение развёрнуто и работает | ✅ | Инструкции ниже + демо-вход в README |
| 2b | Интеграции функционируют | ✅ | См. [`docs/INTEGRATIONS_QA_STEP8.md`](docs/INTEGRATIONS_QA_STEP8.md) |
| 2c | CI/CD пайплайн работает | ✅ | Actions workflow **CI** на push/PR; локальный parity: ruff / pytest / vitest / build |
| **3** | `integration_documentation.md` | ✅ | **этот файл** |
| **4** | `security_audit.md` | ✅ | [`security_audit.md`](security_audit.md) |

\*Критерий курса допускает «ссылка на деплой **или** инструкции» ([#34](https://github.com/Sintik1/Qa_Asistant/issues/34)). Gate **G2=C**: CI-only, без автодеплоя на PaaS.

### Шаги ДЗ 1–9 → артефакты

| Шаг | Тема | Issue | Артефакт |
|-----|------|-------|----------|
| 1 | CI/CD | [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) | §1, `.github/workflows/ci.yml` |
| 2 | Security audit | [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) | `security_audit.md` |
| 3 | OAuth2 | [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) | §2.1, `docs/OAUTH_SETUP.md` |
| 4 | Аналитика | [#41](https://github.com/Sintik1/Qa_Asistant/issues/41) | §2.2, `docs/METRIKA_SETUP.md` |
| 5 | Платежи | — | **skipped** (G7) |
| 6 | Мониторинг | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | §4, `docs/UPTIME_SETUP.md` |
| 7 | Логирование | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | §5, `docs/LOGGING.md` |
| 8 | Тесты + оптимизация | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | `docs/INTEGRATIONS_QA_STEP8.md` |
| 9 | Оформление | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | этот файл + README |

---

## 1. Описание настроек CI/CD

### 1.1. Платформа

- **GitHub Actions** (gate G1=A)
- Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Триггеры: `push` / `pull_request` на `main`|`master`, `workflow_dispatch`
- **Auto-deploy отключён** (`deploy` job с `if: false`) — G2=C (локальный Flask + Ollama)

### 1.2. Stages

| Job | Этапы |
|-----|--------|
| **frontend** | `npm ci` → `npm audit --audit-level=high` → lint (oxlint) → Vitest → `npm run build` |
| **backend** | pip install → `pip-audit` → Ruff check/format → Pytest (`-m "not ui and not security"`) |
| **deploy** | placeholder, **не выполняется** |

Backend CI env: `FLASK_ENV=testing`, `PERSIST_BACKEND=memory`, `EMBEDDING_PROVIDER=hash`.

### 1.3. Локальный прогон (как в Actions)

```bash
# Frontend
cd qa-assistant && npm ci && npm run lint && npm run test && npm run build

# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check app core infrastructure integrations wsgi.py
ruff format --check app core infrastructure integrations wsgi.py
python -m pytest tests/ -m "not ui and not security" \
  --ignore=tests/test_ui_e2e.py --ignore=tests/test_security.py -q
```

Проверка на GitHub: репозиторий → **Actions** → workflow **CI**.

### 1.4. Пример конфигурации (фрагмент)

```yaml
# .github/workflows/ci.yml (сокращённо)
name: CI
on:
  push: { branches: [main, master] }
  pull_request: { branches: [main, master] }
  workflow_dispatch:
jobs:
  frontend:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: qa-assistant } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: npm }
      - run: npm ci
      - run: npm audit --audit-level=high
      - run: npm run lint && npm run test && npm run build
  backend:
    runs-on: ubuntu-latest
    env:
      FLASK_ENV: testing
      PERSIST_BACKEND: memory
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements-dev.txt
      - run: pip-audit -r requirements.txt
      - run: ruff check app core infrastructure integrations wsgi.py
      - run: python -m pytest tests/ -m "not ui and not security" -q
  deploy:
    if: false   # G2=C — no auto-deploy
    needs: [frontend, backend]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploy skipped"
```

Полный файл: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## 2. Инструкции по интеграции сервисов

### 2.1. OAuth2 (Google + Yandex)

Полный гайд: [`docs/OAUTH_SETUP.md`](docs/OAUTH_SETUP.md) · Issue [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)

| Провайдер | Flow |
|-----------|------|
| Google | FE → `GET /api/auth/oauth/google/start` → Google → Flask callback → Supabase session → `/auth/callback#tokens` |
| Yandex | Аналогично через `/api/auth/oauth/yandex/*` |

**Секреты (только `.env`, не VITE_*):**

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
YANDEX_CLIENT_ID=...
YANDEX_CLIENT_SECRET=...
SUPABASE_SERVICE_ROLE_KEY=...   # server-only
OAUTH_API_PUBLIC_URL=http://127.0.0.1:5001
OAUTH_PUBLIC_APP_URL=http://127.0.0.1:5173
```

Redirect URI Google (точно): `http://127.0.0.1:5001/api/auth/oauth/google/callback`  
Проверка: `curl -s http://127.0.0.1:5001/api/auth/oauth/status | jq`  
Тесты: `pytest tests/test_oauth.py -q`

### 2.2. Аналитика (Яндекс.Метрика)

Гайд: [`docs/METRIKA_SETUP.md`](docs/METRIKA_SETUP.md) · Issue [#41](https://github.com/Sintik1/Qa_Asistant/issues/41)

```env
# qa-assistant/.env.local
VITE_YANDEX_METRIKA_ID=113444012
```

Код: `qa-assistant/src/analytics/metrika.ts`, `MetrikaRouteTracker` (SPA `hit`), goals: `auth_login`, `generate_success`, …  
Тесты: `npm test -- src/analytics/metrika.test.ts`

### 2.3. Платежи

**Не интегрированы** (gate G7 — пропуск). В ТЗ продукта нет платежей.

### 2.4. Supabase (Auth / DB / Storage)

Уже в стеке Backend ДЗ. Env: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`.  
Подробнее: [`backend_documentation.md`](backend_documentation.md).

### 2.5. AI (Ollama / Leopold)

```env
AI_PROVIDER=ollama
QA_ASISTANT_API_URL=http://localhost:11434/v1/chat/completions
QA_ASISTANT_MODEL=qwen2.5:1.5b
```

---

## 3. Отчёт по аудиту безопасности

**Файл сдачи:** [`security_audit.md`](security_audit.md)

Кратко:

- Найдено: High по flask-cors + Medium (headers, admin analyze-logs)
- Исправлено: deps, security headers, admin token gate, CI audits, cleanup localStorage token
- Рекомендации: см. `security_audit.md` §3

---

## 4. Мониторинг

Гайд: [`docs/UPTIME_SETUP.md`](docs/UPTIME_SETUP.md)

| Компонент | Описание |
|-----------|----------|
| `GET /api/health` | `status` + блок `checks` (app, disk, db, ai) |
| UptimeRobot | Free HTTP(S) / keyword monitor на публичный URL health (когда появится) |
| Local (G2=C) | `python scripts/watch_health.py` |

Пример ответа:

```json
{
  "status": "ok",
  "api": "qa-assistant",
  "persist": "supabase",
  "checks": {
    "app": { "ok": true },
    "disk": { "ok": true, "path": "uploads", "free_mb": 1234 },
    "db": { "ok": true, "mode": "supabase", "ping": "ok" },
    "ai": { "ok": true, "configured": true, "provider": "ollama" }
  }
}
```

Тесты: `tests/test_health_monitoring.py`.

---

## 5. Логирование

Гайд: [`docs/LOGGING.md`](docs/LOGGING.md)

| Параметр | Значение |
|----------|----------|
| Формат | JSON lines (`service`, `env`, `event`, `request_id`, …) |
| Destination | stdout + rotating `logs/app.log` |
| AI-анализ | `tools/analyze_logs.py --scenario auth\|cors\|ai\|persist\|general` |
| API | `POST /api/admin/analyze-logs` (+ `X-Admin-Token`) |
| Redact | Bearer JWT / `sb_secret_*` до модели |

```env
LOG_LEVEL=INFO
LOG_JSON=1
LOG_TO_FILE=1
LOG_SERVICE=qa-assistant
LOG_ANALYZE_ENABLED=1
LOG_ANALYZE_ADMIN_TOKEN=change-me-local-admin
```

Тесты: `tests/test_logging_and_errors.py`.

---

## 6. Примеры конфигураций (сводка)

| Файл | Назначение |
|------|------------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | CI/CD |
| [`.env.example`](.env.example) | Backend / OAuth / logging / AI placeholders |
| [`qa-assistant/.env.example`](qa-assistant/.env.example) | `VITE_*` (API URL, Metrika id) |
| [`pyproject.toml`](pyproject.toml) | Ruff |
| [`docker-compose.yml`](docker-compose.yml) | UI-only compose (не полный стек) |

---

## 7. Как запустить приложение (вместо публичного деплоя)

1. Скопировать `.env.example` → `.env`, заполнить Supabase + (опц.) OAuth / Metrika.  
2. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`  
3. Flask: `flask --app wsgi run -p 5001` (или `python scripts/run_app.py`)  
4. FE: `cd qa-assistant && npm ci && npm run dev` → http://127.0.0.1:5173  
5. Демо-вход: см. корневой [`README.md`](README.md)  
6. Скринкаст: [`docs/screencast/`](docs/screencast/)

Опциональный публичный деплой (когда появится бюджет/Leopold): FE → Vercel; API → Railway/Render; в CI снять `if: false` у `deploy`.

---

## 8. Тестирование интеграций (шаг 8)

Отчёт: [`docs/INTEGRATIONS_QA_STEP8.md`](docs/INTEGRATIONS_QA_STEP8.md)

- Pytest CI-subset: **121+** · Vitest: **87+**  
- Live: Metrika + Yandex OAuth PASS; Google — проверить redirect URI в Console  

---

_Последнее обновление: 2026-10-06 — шаг 9 оформления результатов._
