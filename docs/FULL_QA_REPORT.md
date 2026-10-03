# Единый отчёт по тестированию — Backend ДЗ шаг 8 (Full QA)

| Поле | Значение |
|------|----------|
| Проект | QA Assistant (Frontend React + Flask hybrid C + Supabase) |
| Репозиторий | https://github.com/Sintik1/Qa_Asistant |
| Дата | 2026-10-03 |
| Issues | [#29](https://github.com/Sintik1/Qa_Asistant/issues/29), [#30](https://github.com/Sintik1/Qa_Asistant/issues/30), [#31](https://github.com/Sintik1/Qa_Asistant/issues/31), [#32](https://github.com/Sintik1/Qa_Asistant/issues/32) |
| Стенд FE | `http://127.0.0.1:5173` |
| Стенд API | `http://127.0.0.1:5001` (`persist=supabase`; порт **5000** занят AirTunes) |
| AI | Ollama `qwen2.5:1.5b` |
| Supabase | `revyywfeeqdmlgrbakpj` |
| Вердикт | **PASS** — API live 23/23; UI happy path; Auth layout; DB persistence (API+UI); Pytest green |

Детальные сырые артефакты (сохранены):  
`docs/API_LIVE_TEST_REPORT.md`, `docs/UI_HAPPY_PATH_REPORT.md`, `docs/DB_PERSISTENCE_TEST_REPORT.md`.  
Исторический UI/адаптив (сентябрь): `docs/TESTING_REPORT.md`.

---

## 1. Scope и методика

Согласованная методика (gate → исполнение):

1. Preflight (Flask / Vite / Ollama / env)
2. Live API matrix (positive + negative / error contract)
3. AI-отладка при fail (логи, CORS, SQL/статусы)
4. Chrome DevTools UI happy path (+ Auth)
5. Проверка записи в Supabase при регистрации и генерации
6. Автотесты бизнес-логики (Pytest)

Вне scope: нагрузочное тестирование, pixel-perfect Figma, физические устройства.

---

## 2. Инструменты

| Инструмент | Роль |
|------------|------|
| `scripts/live_api_full_qa.py` | Live matrix всех Flask endpoints |
| Chrome DevTools MCP | UI Auth + generate + network/console |
| Supabase MCP (`execute_sql`) | Проверка/сид пользователей и строк БД |
| Pytest | Unit/API/business (`tests/`) |
| Ollama | Реальная генерация кейсов |

---

## 3. Сводка результатов

| Блок | Метрика | Итог |
|------|---------|------|
| Live API | 23 / 23 | **PASS** |
| UI happy path (без Auth, bypass) | upload → generate → CSV; reject `.exe` | **PASS** |
| Auth UI layout | `/auth` без вкладок; после login — `AppLayout` | **PASS** |
| DB persistence | PostgREST repos; signup/profile; docs/runs/cases | **PASS** |
| Autonomous API+UI+DB | user SQL-seed; UI login+generate; SQL counts | **PASS** |
| Pytest (выборка после wiring) | 47–59 (в разных прогонах suite) | **PASS** |

---

## 4. API — live matrix

**Команда:** `python scripts/live_api_full_qa.py http://127.0.0.1:5001`  
**Отчёт:** `docs/API_LIVE_TEST_REPORT.md`  
**Итог:** pass=**23**, fail=**0**

### Positive

| Endpoint | HTTP | Примечание |
|----------|------|------------|
| `GET /api/health` | 200 | + `persist`, `.ai` |
| `POST /api/ai/ping` | 200 | Ollama |
| `POST/GET /api/documents`, `GET …/<id>` | 201/200 | meta CRUD |
| `POST /api/documents/upload` | 201 | md + docx extract |
| `POST/GET /api/runs`, `GET …/<id>` | 201/200 | |
| `POST …/generate` | 200 | cases ≥1 |
| `GET …/test-cases`, `PATCH /api/test-cases/<id>` | 200 | |
| `GET/PATCH /api/settings` | 200 | |
| `POST /api/admin/analyze-logs` | 200 | поле `analysis` |
| `DELETE /api/runs/<id>` | 204 → GET 404 | |

### Negative / error contract

| Сценарий | HTTP / code |
|----------|-------------|
| Без auth (`X-Skip-Auth`) | 401 `UNAUTHORIZED` |
| `virus.exe` / upload exe | 422 `INVALID_FORMAT` |
| Файл слишком большой | 422 `FILE_TOO_LARGE` |
| Несуществующий case | 404 |

---

## 5. UI — Chrome DevTools

### 5.1 Happy path (до полного Auth)

См. `docs/UI_HAPPY_PATH_REPORT.md`.

- Health/settings → upload md → generate (3 кейса) → «Скачать CSV»
- Console errors: нет
- Reject `.exe` → TZ alert

### 5.2 Auth UX ([#30](https://github.com/Sintik1/Qa_Asistant/issues/30))

| Проверка | Результат |
|----------|-----------|
| `/` без сессии → `/auth` | PASS |
| На `/auth` нет вкладок Home/Settings | PASS (`AuthLayout`) |
| После login — nav + email + «Выйти» | PASS |
| Generate из UI после login | PASS (8 кейсов в одном прогоне) |

Network (UI с JWT):  
`auth/token` 200 → `upload` 201 → `runs` 201 → `generate` 200.

---

## 6. База данных / интеграция ([#31](https://github.com/Sintik1/Qa_Asistant/issues/31))

### 6.1 Gap и фикс

| Было | Стало |
|------|--------|
| Flask только **in-memory** → 0 rows в Supabase | PostgREST repos (`supabase_rest` / `supabase_store`) |
| | `PERSIST_BACKEND=auto`, JWT → RLS |
| | Mapping статусов: `extracted↔parsed`, `completed↔done`, `generating↔calling_ai` |
| | Health: `"persist": "supabase"` |

### 6.2 Регистрация

| Проверка | Результат |
|----------|-----------|
| Создание `auth.users` | PASS |
| Trigger → `profiles` + `user_settings` | PASS |
| Confirm email в проекте включён | Да (блокирует login без confirm) |
| Публичный signup | 429 rate limit при частых попытках |

### 6.3 Happy path → таблицы

Автономный пользователь `f1197f74-9e80-4da7-a616-e2460cfcb1b7` (`qa.auto…@qatest.local`, SQL-seed confirmed):

| Таблица | Count (итог) | Статус |
|--------|--------------|--------|
| `documents` | **2** (`persist_reqs.md`, `ui_auto_reqs.md`) | PASS |
| `generation_runs` | **2** | PASS |
| `test_cases` | **10** | PASS |
| `profiles` / `user_settings` | 1 / 1 | PASS |

Ранее: пользователь `020b6667-…` — documents/run/cases также PASS (см. `DB_PERSISTENCE_TEST_REPORT.md`).

---

## 7. Найденные проблемы и решения

| # | Проблема | Решение | Issue |
|---|----------|---------|-------|
| 1 | macOS AirTunes на `:5000` | Flask + `VITE_API_BASE_URL` → **5001** | #29 |
| 2 | CORS только `localhost`, UI на `127.0.0.1` | `CORS_ORIGINS` включает оба | #29 |
| 3 | Process env перекрывал `.env.local` Vite | `env -u VITE_*` при старте | #29 |
| 4 | Нет Auth без `VITE_SUPABASE_*` | Ключи в `.env.local` | #29 |
| 5 | `/auth` внутри вкладок AppNav | `AuthLayout` отдельно | #30 |
| 6 | Flask не писал в Supabase | PostgREST repositories | #31 |
| 7 | Enum mismatch domain↔DB | Mapping в `supabase_store` | #31 |
| 8 | Email confirm / signup 429 | SQL confirm/seed + JWT E2E | #31 |
| 9 | Редкий `API_EMPTY` от 1.5b | Retry generate | #31 |

### Известный non-blocker

Модель `qwen2.5:1.5b` иногда заполняет `Step` JSON-подобным шумом. Пайплайн и запись в БД рабочие; качество текста зависит от модели.

---

## 8. Автотесты

| Набор | Результат |
|-------|-----------|
| `tests/test_business_logic_full.py` | happy path + errors + bypass |
| `tests/test_supabase_status_mapping.py` | mapping + `PERSIST_BACKEND` |
| API smoke / generate / upload / auth / error / logging | green в прогонах после фиксов |
| Скрипты live | `scripts/live_api_full_qa.py`, `scripts/live_db_happy_path.py` |

Pytest: memory path для unit; live — отдельный прогон против Flask+Supabase.

---

## 9. Артефакты кода (тестовый цикл)

| Артефакт | Назначение |
|----------|------------|
| `infrastructure/supabase_rest.py` | PostgREST client (JWT/RLS) |
| `infrastructure/supabase_store.py` | Document/Run/Case/Settings repos |
| `qa-assistant/.../AuthLayout.tsx` | Auth без вкладок |
| `tests/fixtures/live_qa/` | md/docx/exe fixtures |
| `PERSIST_BACKEND` в `.env.example` | `auto` / `supabase` / `memory` |

---

## 10. Как воспроизвести

```bash
# API (не :5000 на macOS)
cd /path/to/repo
source .venv/bin/activate
set -a && source .env && set +a   # SUPABASE_*, PERSIST_BACKEND=auto
AUTH_DEV_BYPASS=1 flask --app wsgi run -p 5001 --host 127.0.0.1

# FE
cd qa-assistant
# .env.local: VITE_API_BASE_URL=http://127.0.0.1:5001 + VITE_SUPABASE_*
env -u VITE_API_BASE_URL npm run dev -- --host 127.0.0.1 --port 5173

# Live API
python scripts/live_api_full_qa.py http://127.0.0.1:5001

# DB happy path (нужен confirmed user / JWT)
QA_E2E_LOGIN_ONLY=1 QA_E2E_EMAIL=... QA_E2E_PASSWORD=... \
  python scripts/live_db_happy_path.py http://127.0.0.1:5001

# Pytest
pytest tests/test_business_logic_full.py tests/test_api_*.py \
  tests/test_auth_jwt.py tests/test_supabase_status_mapping.py -q
```

---

## 11. Вердикт и рекомендации

**Вердикт: PASS** для Backend ДЗ шаг 8 (Full QA + persistence + Auth UX).

Рекомендации:

1. Для демо отключить **Confirm email** в Supabase Auth или завести `SUPABASE_SERVICE_ROLE_KEY` (admin confirm + Storage).
2. Держать локальный API на **5001** на macOS.
3. Для CI оставлять `PERSIST_BACKEND=memory` / `testing=True`; live Supabase — отдельный job/скрипт.
4. При сдаче (шаг 9) приложить этот файл как основной отчёт по тестированию.

---

_Составлено: 2026-10-03. Issue единого отчёта: [#32](https://github.com/Sintik1/Qa_Asistant/issues/32)._
