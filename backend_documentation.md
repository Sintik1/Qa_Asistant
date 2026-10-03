# Backend Documentation — QA Assistant (ДЗ: БД, Supabase, API)

Документ — **артефакт сдачи домашнего задания** и живой журнал backend-разработки. Обновляется **на каждом шаге ДЗ** (1–9) в том же цикле, что и GitHub Issue и краткая запись в `development_report.md`.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

**Согласованный режим работы:** пользователь присылает отдельный промпт на шаг ДЗ → агент выполняет шаг → фиксирует результат здесь (и в Issue / `development_report.md`).

**Инфраструктурный выбор:** **Supabase (BaaS)** — принято на шаге 2 ДЗ ([#21](https://github.com/Sintik1/Qa_Asistant/issues/21)); Flask — доменный API (upload, generate, Leopold); React — Supabase Client + Flask где нужно. Self-hosted Postgres/VPS — отклонён (см. §2.0).

---

## Содержание

1. [Описание архитектуры](#1-описание-архитектуры)
2. [Инструкции по развертыванию](#2-инструкции-по-развертыванию)
3. [Описание API endpoints](#3-описание-api-endpoints)
4. [Примеры запросов](#4-примеры-запросов)
5. [Процесс разработки с AI](#5-процесс-разработки-с-ai)
6. [Журнал шагов ДЗ](#6-журнал-шагов-дз)

---

## 1. Описание архитектуры

### 1.1. Контекст продукта

QA Assistant: загрузка документов требований → извлечение текста → чанкинг → вызов ИИ (Leopold / Qwen) → CSV / табличные тест-кейсы для TestRail/Zephyr.

### 1.2. Целевая схема (после выполнения ДЗ)

```text
┌─────────────┐     JWT (Supabase Auth)      ┌──────────────────┐
│  React UI   │◄────────────────────────────►│  Supabase        │
│ qa-assistant│     PostgREST / Client       │  Auth + Postgres │
└──────┬──────┘                              │  + Storage + RLS │
       │                                      └────────▲─────────┘
       │ HTTP (generate, upload, CRUD proxy)            │
       ▼                                                │ service role
┌─────────────┐         SQL / Storage API              │ (server only)
│ Flask API   │─────────────────────────────────────────┘
│ (Python)    │────► Leopold / external AI API
└─────────────┘
```

### 1.3. Слои приложения (Flask)

| Слой | Ответственность |
|------|-----------------|
| HTTP (routes) | Тонкие handlers, DTO, коды ошибок по ТЗ |
| Application | Use cases: upload, generate, persist run |
| Domain | Правила валидации кейсов, статусы прогона |
| Infrastructure | Supabase client, Storage, Repository, UoW |

### 1.4. Требования к данным (из ТЗ)

| Источник в ТЗ | Что хранить | Приоритет |
|---------------|-------------|-----------|
| Upload PDF/DOCX/DOC/MD ≤100 МБ | метаданные файла + файл в Storage | MUST |
| Extract + chunking | факт извлечения, параметры чанка | MUST / SHOULD |
| Generation + AI debug | прогон, статусы, debug request/response | MUST |
| CSV Name/Status/Step/Expected Result | результат для скачивания и CRUD | MUST |
| API token + chunk settings | настройки пользователя / env | MUST |
| История загрузок | список документов + статус + ссылка на результат | NICE |
| Повторная генерация | тот же document, новый run с другими chunk params | SHOULD |
| DOCX export | опциональный артефакт экспорта | SHOULD |

**Инварианты:** файлы не в git; секреты не в plaintext в репо; RLS по `user_id = auth.uid()`; бинарники — Supabase Storage, в таблицах — пути.

### 1.5. Варианты схем (шаг 1 — выбор пользователя)

> **Gate (закрыт):** выбран **вариант B**. SQL + миграция: `supabase/migrations/20260928143000_init_variant_b.sql`. Issue [#20](https://github.com/Sintik1/Qa_Asistant/issues/20).

#### Вариант A — Minimal MVP (быстрый CRUD для ДЗ)

**Таблицы (4):** `profiles`, `documents`, `generation_runs`, `test_cases`

```text
auth.users 1──1 profiles
profiles   1──N documents
documents  1──N generation_runs
generation_runs 1──N test_cases
```

| Таблица | Ключевые поля |
|---------|----------------|
| `profiles` | `id` PK→auth.users, `display_name`, `created_at` |
| `documents` | `id`, `user_id`, `original_filename`, `mime_type`, `size_bytes`, `storage_path`, `status`, `created_at` |
| `generation_runs` | `id`, `user_id`, `document_id`, `status`, `chunk_size`, `chunk_overlap`, `chunk_method`, `error_message`, `result_csv_path`, `started_at`, `finished_at` |
| `test_cases` | `id`, `run_id`, `user_id`, `name`, `status`, `step`, `expected_result`, `sort_order` |

**Плюсы:** мало таблиц, простое RLS, ≥3 CRUD. **Минусы:** нет `user_settings`; debug только в Storage; чанки не нормализованы.

#### Вариант B — Operational (рекомендуемый под ТЗ + ДЗ)

**Таблицы (6):** A + `user_settings` + `generation_chunks`

```text
profiles 1──1 user_settings
generation_runs 1──N generation_chunks
generation_chunks 1──N test_cases (опциональный FK)
```

| Таблица | Дополнительно к A |
|---------|-------------------|
| `user_settings` | `user_id` PK, `chunk_size`, `chunk_overlap`, `chunk_method`, `has_api_token` (bool; токен — `.env`/Vault), `updated_at` |
| `generation_chunks` | `id`, `run_id`, `chunk_index`, `content_preview` или `storage_path`, `status`, `retry_count`, `raw_response_path`, `error_message` |

**Плюсы:** debug по ТЗ, настройки, retry по чанку, история. **Минусы:** чуть больше миграций/API.

#### Вариант C — Extended (roadmap / learning)

**Таблицы (9–10):** B + `exports` + `prompt_templates` + `feedback` (+ опц. `project_contexts`)

| Таблица | Назначение |
|---------|------------|
| `exports` | CSV/DOCX: `run_id`, `format`, `storage_path`, `row_count` |
| `prompt_templates` | версии DEFAULT/CHUNK system prompts |
| `feedback` | оценка run/case (`rating`, `comment`) |
| `project_contexts` | глоссарий/контекст проекта для промпта |

**Плюсы:** learning loop. **Минусы:** избыточно для MUST MVP и сроков ДЗ.

### 1.6. Сравнение и рекомендация

| Критерий | A | B | C |
|----------|---|---|---|
| Покрытие MUST ТЗ | да (debug через Storage) | да | да |
| История (NICE) | да | да | да |
| Debug как в ТЗ | частично | да | да |
| User settings UI | нет (env) | да | да |
| Сложность / срок ДЗ | низкая | средняя | высокая |

**Рекомендация архитектора:** **вариант B**. C — phase 2.

### 1.7. Выбранная схема — **B Operational** (реализовано)

**Миграция:** [`supabase/migrations/20260928143000_init_variant_b.sql`](supabase/migrations/20260928143000_init_variant_b.sql)

```text
auth.users ──1:1── profiles ──1:1── user_settings
                 │
                 ├──1:N── documents ──1:N── generation_runs
                 │                              │
                 │                              ├──1:N── generation_chunks
                 │                              │              │
                 │                              └──1:N── test_cases ──(N:1 опц.)─┘
```

| Таблица | Поля (кратко) | Связи |
|---------|---------------|--------|
| `profiles` | `id`→auth.users, `display_name`, timestamps | 1:1 user |
| `user_settings` | `user_id`, `chunk_size/overlap/method`, `has_api_token` | 1:1 profile |
| `documents` | filename, mime, `size_bytes`≤100MiB, `storage_path`, `status`, page/chars, error | N:1 user |
| `generation_runs` | document_id, status pipeline, chunk params snapshot, csv path, case_count, times | N:1 document |
| `generation_chunks` | run_id, chunk_index, preview/path, status, retry, raw_response_path | N:1 run; unique(run,index) |
| `test_cases` | name, status, step, expected_result, sort_order, optional chunk_id | N:1 run |

**Корректировки относительно черновика:**
- `user_id` денормализован на `generation_chunks` и `test_cases` → простые RLS-политики.
- Token Leopold **не** в таблице (только `has_api_token`).
- CHECK на размер файла 100 МБ; enums статусов; trigger `on_auth_user_created` → profile + settings.
- Базовый RLS включён в миграции (уточнение Auth/CORS — шаг 5 ДЗ).

### 1.8. Безопасность (шаг 5) — **реализовано (awaiting OK)**

Issue: [#25](https://github.com/Sintik1/Qa_Asistant/issues/25). Выбран **вариант A: Supabase Auth**.

#### Что сделано

| Область | Реализация |
|---------|------------|
| Auth | Supabase Auth email/password; FE `/auth` + `AuthProvider`; signup trigger → profile/settings |
| RLS (tables) | Owner isolation `user_id = auth.uid()` / `id = auth.uid()` (миграция Variant B) |
| RLS (Storage) | Дополнены policies: `debug` update/delete, `exports` update (`20261003183000_security_storage_policies.sql`) |
| Flask JWT | `app/auth.py` — HS256 через `SUPABASE_JWT_SECRET` (fallback: Auth `/user`); `g.user_id` из `sub` |
| Bypass | `X-User-Id` только при `testing=True` или `AUTH_DEV_BYPASS=1` |
| CORS | `CORS_ORIGINS` whitelist; credentials + `Authorization` header |
| Secrets | `.env` / `.gitignore`; anon на FE; `SERVICE_ROLE` / JWT secret / Leopold — только server |

#### Поток

```text
React /auth ──signUp/signIn──► Supabase Auth ──JWT──► localStorage session
React API calls ──Authorization: Bearer <jwt>──► Flask middleware (verify) ──g.user_id──► services
React / PostgREST ──same JWT──► Supabase RLS (auth.uid())
```

#### Локальный запуск Auth

1. Skопировать `.env.example` → `.env` и `qa-assistant/.env.local`.
2. Dashboard → Settings → API: `anon`, `service_role`, **JWT Secret**.
3. `VITE_SUPABASE_*` + `SUPABASE_JWT_SECRET` + `CORS_ORIGINS`.
4. FE: `npm run dev` → `/auth` (регистрация/вход).
5. Flask: `PYTHONPATH=. flask run` — защищённые `/api/*` требуют Bearer JWT.

---

## 2. Инструкции по развертыванию

### 2.0. Выбор инфраструктуры (ДЗ шаг 2) — **принято: вариант A Supabase**

Issue: [#21](https://github.com/Sintik1/Qa_Asistant/issues/21)

#### Требования проекта, влияющие на выбор

| Требование | Источник | Что нужно от инфраструктуры |
|------------|----------|------------------------------|
| Postgres + миграции Variant B | ДЗ шаг 1, ТЗ | Управляемая БД или Docker Postgres |
| Auth (регистрация/вход) | ДЗ шаг 5 | Готовый Auth или своя реализация |
| RLS / изоляция пользователей | ДЗ шаг 5, безопасность | Policies в Postgres или middleware |
| Storage файлов (upload ≤100 МБ, debug, CSV) | ТЗ MUST | Object storage + пути в БД |
| API ≥3 CRUD + доменный generate | ДЗ шаг 4, ТЗ | PostgREST и/или Flask |
| Секреты вне репо | ТЗ / `.cursorrules` | `.env`, не коммитить ключи |
| Срок сдачи ДЗ / учебный scope | ДЗ | Быстрый путь до e2e |
| Уже есть миграция под Supabase | `supabase/migrations/` | Совместимость с Auth schema |

#### Сравнение вариантов

| Критерий | A — Supabase (BaaS) | B — Self-hosted (Postgres Docker на VPS) |
|----------|---------------------|------------------------------------------|
| Postgres + миграции SQL | Да (SQL Editor / CLI) | Да (свой Postgres) |
| Auth из коробки | Supabase Auth | Писать самим (JWT/sessions) |
| RLS | Встроено + Dashboard | Нужен свой middleware + политики вручную |
| Storage | Buckets + policies | S3/MinIO или диск на VPS + свой API |
| REST CRUD | PostgREST автоматически | Только Flask (больше кода) |
| Logs | Supabase Logs | journald / свой стек |
| Стоимость старта | Free tier обычно хватает для ДЗ | VPS (~$/мес) + админ-время |
| Ops-нагрузка | Низкая | Высокая (OS, Docker, TLS, бэкапы, firewall) |
| Соответствие уже сделанной схеме | Триггер на `auth.users`, RLS | Нужен свой `users` + переписать trigger/RLS |
| Риск для сроков ДЗ | Низкий | Высокий (VPS + Auth + Storage + CORS) |

#### Решение

**Выбран вариант A: Supabase (BaaS).**

**Обоснование:**
1. ДЗ явно требует Auth, RLS, CRUD и (по сути) быстрый путь к работающему приложению — это ядро Supabase.
2. Миграция Variant B уже завязана на `auth.users` и RLS — self-hosted потребовал бы перепроектирования.
3. ТЗ требует хранение upload/debug артефактов вне git — Storage Supabase закрывает это без MinIO/VPS.
4. Flask остаётся для Leopold/generate (доменная логика) — гибрид «Supabase persistence + Flask AI» лучше стыкуется с Clean Architecture проекта, чем «голый Postgres + всё писать с нуля».
5. Self-hosted не даёт преимуществ для текущего MVP (один продукт, учебная сдача), но сильно увеличивает ops.

**Вариант B (self-hosted) — не выбран.** Подготовка VPS **не выполняется**. Краткий fallback описан в §2.5 на случай смены требований.

#### Целевая топология (после выбора)

```text
React (Vite) ──JWT──► Supabase Auth / PostgREST / Storage
       │
       └──HTTP──► Flask (upload/generate/Leopold) ──service role──► Supabase
```

### 2.1. Предварительные требования

- Node.js (frontend `qa-assistant/`)
- Python 3.14+ (Flask backend)
- Аккаунт [Supabase](https://supabase.com) — **обязателен** (выбранный путь)
- Cursor MCP `user-supabase` (см. §2.2)
- Supabase CLI (опционально; для ДЗ достаточно MCP)
- VPS **не требуется**

### 2.2. Supabase — проект и MCP (шаг 3)

| Параметр | Значение |
|----------|----------|
| project_ref | `revyywfeeqdmlgrbakpj` |
| API URL | `https://revyywfeeqdmlgrbakpj.supabase.co` |
| MCP server | в `~/.cursor/mcp.json` → namespace `user-supabase` |
| Auth MCP | выполнено (`mcp_auth`) |

**Сделано через MCP:**
1. `apply_migration` → `init_variant_b` (6 таблиц + RLS + signup trigger)
2. `apply_migration` → `harden_auth_triggers` (search_path + revoke EXECUTE)
3. Storage buckets: `documents`, `debug`, `exports` (private) + policies по prefix `auth.uid()`
4. Проверено: `list_tables` — все 6 с `rls_enabled=true`
5. Шаг 5: `apply_migration` → `security_storage_policies` (debug update/delete, exports update)

**Локальные артефакты:**
- `supabase/migrations/20260928143000_init_variant_b.sql`
- `supabase/migrations/20260928140000_harden_auth_triggers.sql`
- `supabase/migrations/20261003183000_security_storage_policies.sql`
- `.env.example` (ключи — плейсхолдеры; реальные — из Dashboard / MCP `get_publishable_keys`)

### 2.3. Переменные окружения

Скопировать `.env.example` → `.env` и `qa-assistant/.env.local` (из `qa-assistant/.env.example`).

| Переменная | Где | Назначение |
|------------|-----|------------|
| `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` | FE | Auth + PostgREST (publishable) |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` | Flask | fallback verify через Auth `/user` |
| `SUPABASE_JWT_SECRET` | Flask | локальная проверка JWT (предпочтительно) |
| `SUPABASE_SERVICE_ROLE_KEY` | Flask only | обход RLS на сервере; **никогда** во FE |
| `CORS_ORIGINS` | Flask | whitelist фронтенда |
| `QA_ASISTANT_API_TOKEN` | Flask | Leopold/Ollama; не в БД |

`SUPABASE_SERVICE_ROLE_KEY` и `SUPABASE_JWT_SECRET` — **только** сервер, никогда во frontend / git.

### 2.4. Локальный запуск

_Позже (шаги 4–6):_ Vite + Flask + этот cloud-проект.

### 2.5. Self-hosted (отклонённый альтернативный путь)

Если когда-либо понадобится полный контроль / air-gap:
1. VPS + Docker Compose: `postgres`, опционально `minio`, Flask, nginx.
2. Переписать signup без `auth.users` (своя таблица `users`).
3. Реализовать Auth + middleware вместо RLS (или RLS вручную).
4. Бэкапы `pg_dump`, TLS, firewall.

**Для текущего ДЗ не используется.**

---

## 3. Описание API endpoints

> **Шаг 4 ДЗ — gate:** варианты ниже; код **не пишем** до одобрения. Issue: создать/обновить «Backend ДЗ шаг 4».

### 3.0. Минимальный контракт CRUD (для любого варианта)

Достаточно для ДЗ (≥3 операции) и истории из ТЗ (NICE):

| Операция | Ресурс | Смысл |
|----------|--------|--------|
| **C**reate | `documents` или `generation_runs` | создать документ / прогон |
| **R**ead | `generation_runs` (+ `test_cases`) | список / детали |
| **U**pdate | `test_cases` или `user_settings` | правка кейса / настроек |
| **D**elete | `generation_runs` или `documents` | удалить прогон / документ |

Домен ТЗ (upload → generate → CSV) — поверх CRUD; Leopold **не** через PostgREST.

### 3.1. Варианты реализации (на выбор)

#### Вариант A — только Supabase REST (PostgREST + Client)

Frontend → `@supabase/supabase-js` / REST напрямую к таблицам. Auth JWT → RLS.

| Плюсы | Минусы |
|-------|--------|
| Быстро закрыть «≥3 CRUD» | Нет единого Flask error contract для generate |
| Меньше кода backend | Upload/AI всё равно нужен отдельный сервер позже |
| RLS из коробки | Сложнее валидировать бизнес-правила ТЗ на сервере |

**Endpoints (PostgREST):**  
`POST/GET/PATCH/DELETE /rest/v1/documents|generation_runs|test_cases|user_settings`

#### Вариант B — только Flask CRUD (+ Supabase как БД)

Frontend → только Flask. Flask с JWT пользователя (или service role + проверка) пишет в Supabase/Postgres через Repository.

| Плюсы | Минусы |
|-------|--------|
| Единый API и ошибки ТЗ | Больше кода на шаге 4 |
| Clean Architecture / Pytest как в `.cursorrules` | Нужен каркас Flask с нуля |
| Готовность к generate на том же сервере | Дублирует часть PostgREST |

**Минимум путей Flask:**  
`POST/GET /api/documents`, `GET/POST /api/runs`, `GET/PATCH/DELETE /api/test-cases/<id>`, `GET/PATCH /api/settings`

#### Вариант C — гибрид (рекомендация)

- **CRUD истории / settings / test_cases** — Supabase Client (PostgREST + RLS)  
- **Домен** upload / generate / export / Leopold — Flask  
- Единый error JSON на Flask; на Supabase — HTTP-коды + маппинг на FE

| Плюсы | Минусы |
|-------|--------|
| Совпадает с уже выбранной infra (шаг 2) | Два клиента на FE (Supabase + Flask) |
| Быстрый CRUD для ДЗ + путь к AI | Нужна дисциплина: секреты только Flask |
| Соответствует skills api/backend/data | Чуть сложнее docs |

### 3.2. Рекомендуемый набор endpoints (если C)

**Supabase REST (автоматический):**

| Метод | Таблица | CRUD |
|-------|--------|------|
| `GET` | `generation_runs` | R |
| `POST` | `generation_runs` | C |
| `PATCH` | `test_cases` | U |
| `DELETE` | `generation_runs` | D |

**Flask (свой API, каркас на шаге 4 или 4+generate):**

| Метод | Path | Назначение |
|-------|------|------------|
| `GET` | `/api/health` | health |
| `POST` | `/api/documents` | upload + meta в Supabase Storage/DB |
| `POST` | `/api/runs/<id>/generate` | пайплайн AI (можно stub на шаге 4) |
| `GET` | `/api/runs/<id>/export.csv` | CSV |

### 3.3. Обработка ошибок (обязательно во всех вариантах)

Единый JSON (как `qa-assistant-api`):

```json
{ "error": { "code": "INVALID_FORMAT", "message": "…текст из ТЗ…" } }
```

| Класс | HTTP | Примеры `code` | Сообщение |
|-------|------|----------------|-----------|
| Валидация | 400 / 422 | `INVALID_FORMAT`, `FILE_TOO_LARGE`, `EMPTY_FILE`, `CORRUPT_FILE` | `ERROR_MESSAGES` FE |
| Бизнес / данные | 404 / 422 | `NO_REQUIREMENTS`, `NOT_FOUND`, `INVALID_CSV` | ТЗ |
| Auth | 401 / 403 | `UNAUTHORIZED`, `FORBIDDEN`, `MISSING_TOKEN`, `INVALID_TOKEN` | ТЗ / JWT |
| Внешний AI | 502 / 503 / 429 | `API_UNAVAILABLE`, `API_503`, `API_429`, `API_EMPTY` | ТЗ |
| Сервер | 500 | `INTERNAL_ERROR` | без stack/token leak |

Дополнительно: CORS errors → понятный FE fallback; network timeout → retry UX (шаг 7).

### 3.4. Выбранный вариант API — **C (реализовано)**

Issue: [#23](https://github.com/Sintik1/Qa_Asistant/issues/23)

**AI (два режима):**
| Режим | Когда | Модель | Env |
|-------|-------|--------|-----|
| **ollama** (default для учёбы) | локальная отладка | **M1 8GB → `qwen2.5:1.5b`**; опц. `3b` | `AI_PROVIDER=ollama`, `AI_OLLAMA_SIZE=1.5b` |
| **leopold** | ТЗ / «прод» | `Qwen/Qwen2.5-72B-Instruct` | `AI_PROVIDER=leopold` + URL/token |

Код: `integrations/ai_client.py` (OpenAI-compatible), `integrations/leopold_client.py` (обёртка).  
Скрипт: `scripts/setup_ollama.sh [7b|14b]`.  
Smoke: `POST /api/ai/ping`, статус в `GET /api/health` → `.ai`.

**Flask endpoints (свой API):**

| Метод | Path | CRUD / роль | Статус |
|-------|------|-------------|--------|
| `GET` | `/api/health` | health + ai config (provider/model) | done |
| `POST` | `/api/ai/ping` | smoke-вызов Ollama/Leopold | done |
| `POST` | `/api/documents` | **C**reate document meta | done |
| `GET` | `/api/documents` | **R**ead list | done |
| `GET` | `/api/documents/<id>` | **R**ead one | done |
| `POST` | `/api/runs` | **C**reate run | done |
| `GET` | `/api/runs` | **R**ead list | done |
| `GET` | `/api/runs/<id>` | **R**ead one | done |
| `DELETE` | `/api/runs/<id>` | **D**elete | done |
| `GET` | `/api/runs/<id>/test-cases` | **R**ead cases | done |
| `PATCH` | `/api/test-cases/<id>` | **U**pdate case | done |
| `GET`/`PATCH` | `/api/settings` | settings | done |
| `POST` | `/api/runs/<id>/generate` | AI generate → cases | done (шаг 6) |

**Supabase REST (автоматический, параллельно для FE):**  
`GET/POST/PATCH/DELETE https://revyywfeeqdmlgrbakpj.supabase.co/rest/v1/{documents|generation_runs|test_cases|user_settings}` + JWT + RLS.

**Запуск:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi run -p 5000
# tests:
pytest tests/test_api_smoke.py tests/test_api_error_contract.py -q
```

Текущий persistence Flask-слоя: **in-memory repositories** (pytest/local). Подключение Flask→Supabase PostgREST service role — следующий инкремент (Auth шаг 5).

### 3.5. Формат ошибок (реализовано)

```json
{ "error": { "code": "INVALID_FORMAT", "message": "Поддерживаются только PDF, DOCX, DOC и Markdown-файлы" } }
```

Коды: `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`, `INVALID_FORMAT`, `FILE_TOO_LARGE`, `MISSING_TOKEN`, `INVALID_TOKEN`, `API_*`, `INTERNAL_ERROR`.

---

## 4. Примеры запросов

### 4.0. Ollama + Qwen (учёба) — MacBook Air M1 8GB

**Выбор модели:** `qwen2.5:1.5b` (~1 GB). Не ставить 7B/14B на 8GB.  
**macOS 13 Ventura:** свежий Ollama.app (0.35+) требует macOS 14 — скрипт ставит **Ollama v0.6.5** в `~/.local/ollama-v0.6.5`.

```bash
./scripts/setup_ollama.sh 1.5b
# держать сервер: ollama serve   (PATH: ~/.local/bin)
cp .env.example .env   # модель уже 1.5b

source .venv/bin/activate
flask --app wsgi run -p 5000

curl -s http://localhost:5000/api/health | jq .ai
curl -s -X POST http://localhost:5000/api/ai/ping \
  -H 'Content-Type: application/json' -d '{"prompt":"ping"}' | jq
```

### 4.1. Health

```bash
curl -s http://localhost:5000/api/health | jq
```

### 4.2. CRUD (Flask)

```bash
# Create document
curl -s -X POST http://localhost:5000/api/documents \
  -H 'Content-Type: application/json' -H 'X-User-Id: 11111111-1111-4111-8111-111111111111' \
  -d '{"original_filename":"reqs.md","size_bytes":120}' | jq

# Create run (подставьте DOCUMENT_ID)
curl -s -X POST http://localhost:5000/api/runs \
  -H 'Content-Type: application/json' -H 'X-User-Id: 11111111-1111-4111-8111-111111111111' \
  -d '{"document_id":"DOCUMENT_ID","chunk_method":"header"}' | jq

# List runs
curl -s http://localhost:5000/api/runs -H 'X-User-Id: 11111111-1111-4111-8111-111111111111' | jq

# Update test case
curl -s -X PATCH http://localhost:5000/api/test-cases/CASE_ID \
  -H 'Content-Type: application/json' -H 'X-User-Id: 11111111-1111-4111-8111-111111111111' \
  -d '{"step":"1. Open app"}' | jq

# Delete run
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE \
  http://localhost:5000/api/runs/RUN_ID \
  -H 'X-User-Id: 11111111-1111-4111-8111-111111111111'

# Generate (нужен AI: Ollama/Leopold; в тестах — FakeAi)
curl -s -X POST http://localhost:5000/api/runs/RUN_ID/generate \
  -H 'Content-Type: application/json' -H 'X-User-Id: 11111111-1111-4111-8111-111111111111' \
  -d '{"requirements_text":"User can log in.","task_name":"Auth"}' | jq
```

### 4.3. Auth (Supabase)

SignUp / SignIn — шаг 5 ДЗ. Flask CRUD: `Authorization: Bearer <jwt>` (prod); `X-User-Id` только testing / `AUTH_DEV_BYPASS`.

### 4.4. Frontend ↔ API (шаг 6) — **реализовано (вариант B, awaiting OK)**

Issue: [#26](https://github.com/Sintik1/Qa_Asistant/issues/26)

**Выбрано:** вариант **B** (полный happy-path). Axios не добавлялся.

#### Backend

| Метод | Path | Назначение |
|-------|------|------------|
| `POST` | `/api/runs/<id>/generate` | AI → parse CSV cases → persist; body: `requirements_text`, `task_name`, `prompt` |

Код: `core/services.py` (`GenerationService`), `core/case_parser.py`, thin route в `app/routes.py`.  
Pytest: `tests/test_api_generate.py`, `tests/test_case_parser.py` (+ smoke/error/auth) — **24 passed**.

#### Frontend

| Артефакт | Роль |
|----------|------|
| `qa-assistant/src/api/*` | typed client: documents, runs, settings, errors |
| `hooks/useTestCaseGeneration.ts` | document → run → generate → UI cases (без mock) |
| `hooks/useSettingsApi.ts` | GET/PATCH settings |
| `HomePage` / `SettingsPage` | реальные данные; mock hint убран |
| Клиент | `@supabase/supabase-js` + `apiFetch` (Bearer JWT) |

**Поток:** validate file → read text (.md) / metadata stub (pdf/docx) → `POST /api/documents` → `POST /api/runs` → `POST …/generate` → CSV download как раньше.

**Ограничения шага:** multipart Storage upload и серверный extract PDF/DOCX — следующие инкременты; Leopold token остаётся в server `.env`, UI ставит `has_api_token`.

---

## 5. Процесс разработки с AI

### 5.1. Роль AI-агента

Senior Python Developer: проектирование схемы, миграции, Flask API, интеграция с Supabase; ревью SQL и RLS; генерация тестов и документации.

### 5.2. Workflow на каждый шаг ДЗ

1. Пользователь — промпт с номером шага (1–9) и scope.
2. Агент — Issue в GitHub (если новый шаг) + выполнение + обновление **этого файла** (разделы 1–4 по необходимости, раздел 6 — всегда).
3. Агент — **полное** обновление `development_report.md` по `.cursorrules` §11 (не только журнал: процесс, техники AI, промпты, проблемы, выводы + строка журнала со ссылкой сюда).
4. Код и инфраструктура — по **всем** правилам проекта: Repository/UoW, Pytest, API-контракт, без секретов в репо, scope ТЗ/Figma; skills `qa-assistant-*` по области задачи.
5. Коммит — только по запросу пользователя.

### 5.2.1. Что не отменяется на backend ДЗ

| Область | Источник |
|---------|----------|
| Issues + `development_report.md` | `.cursorrules` §10–11 |
| Архитектура, SQL, секреты, тесты | `.cursorrules` §5–9, §17, §19–20 |
| Backend/API/data | skills backend, data, api, testing |
| Frontend (шаги 6–8) | skills ui, react; UI rules |
| Трекинг backend артефакта | `.cursorrules` §12, `backend-homework-dz.mdc` |

### 5.4. Шаг 6 — промпт и результат

**Запрос:** Senior FullStack; клиент, хуки, load/send, убрать mock; сначала решение → после OK код → коммит. Затем выбор **`b`**.

**Результат:** Issue [#26](https://github.com/Sintik1/Qa_Asistant/issues/26).
- FE: `src/api/*`, `useTestCaseGeneration` / `useSettingsApi` на Flask
- BE: `POST /api/runs/<id>/generate` + `case_parser`
- Pytest API+parser+auth: **24 passed**
- Vitest: npm недоступен в среде агента — прогон локально у пользователя
- Коммит — после явной просьбы

### 5.3. Применённые техники (накопительно)

| Техника | Когда |
|---------|--------|
| Архитектурное обсуждение без кода | План Supabase, ER, scope ДЗ |
| Role/Task/Context/Format + варианты схем | Шаг 1 ДЗ: 3 варианта до миграций (gate) |
| Mapping ТЗ → сущности | MUST/SHOULD/NICE → таблицы |
| Decision matrix infra A vs B | Шаг 2 ДЗ: требования → выбор Supabase |
| MCP auth + remote apply_migration | Шаг 3: `user-supabase` → project `revyywfeeqdmlgrbakpj` |

### 5.4. Примеры промптов и результатов

#### Промпт: согласование режима ДЗ + `backend_documentation.md`

**Запрос:** по каждому шагу ДЗ отдельные промпты; фиксация в `backend_documentation.md` (архитектура, деплой, API, примеры, AI-процесс); при необходимости — правки cursorrules.

**Результат:** создан каркас `backend_documentation.md`; добавлены `.cursorrules` §12 и правило `.cursor/rules/backend-homework-dz.mdc`; предварительная архитектура Supabase + Flask + React.

#### Промпт: Шаг 1 ДЗ — проектирование БД (варианты)

**Запрос:** Role архитектор БД; Task — сущности/связи/поля, SQL, миграции; Context — ТЗ + project_description; Format — сначала 2–3 варианта на выбор.

**Результат:** Issue [#20](https://github.com/Sintik1/Qa_Asistant/issues/20). Варианты A/B/C; gate до выбора.

#### Промпт: выбор B + миграции

**Запрос:** `b`

**Результат:** зафиксирован Variant B; миграция `supabase/migrations/20260928143000_init_variant_b.sql` (6 таблиц, enums, RLS, trigger signup); документация §1.7 обновлена.

#### Промпт: Шаг 2 ДЗ — выбор инфраструктуры

**Запрос:** выбрать A Supabase vs B self-hosted Postgres на VPS; обосновать; VPS готовить только если B.

**Результат:** Issue [#21](https://github.com/Sintik1/Qa_Asistant/issues/21). Выбран **A Supabase**. VPS не готовится. Обоснование и сравнение — §2.0.

#### Промпт: MCP + развёртывание на существующем проекте

**Запрос:** настроить MCP с `project_ref=revyywfeeqdmlgrbakpj` и подключиться для дальнейшей работы.

**Результат:** Issue [#22](https://github.com/Sintik1/Qa_Asistant/issues/22).
- `~/.cursor/mcp.json` + auth `user-supabase`
- URL: `https://revyywfeeqdmlgrbakpj.supabase.co`
- Миграции на cloud: `init_variant_b`, `harden_auth_triggers`
- Buckets + storage policies; `.env.example`

#### Промпт: Шаг 4 ДЗ — API (варианты → C → реализация)

**Запрос:** варианты API; затем `с` + вопрос про Qwen; «продолжай».

**Результат:** Issue [#23](https://github.com/Sintik1/Qa_Asistant/issues/23).
- Выбран **C**; Qwen — да (ТЗ / Leopold)
- Flask: `app/`, `core/`, `infrastructure/`, `integrations/leopold_client.py`
- Pytest: **8 passed** (`test_api_smoke`, `test_api_error_contract`)
- Docs §3.4–§4

### 5.5. Проблемы и решения

| Проблема | Решение |
|----------|---------|
| Риск over-engineering схемы под learning JSON | Разделить A/B/C; выбран B |
| Токен Leopold в БД vs ТЗ «только .env» | Только `has_api_token`; plaintext не в Postgres |
| RLS на child-таблицах через join | Денормализация `user_id` на chunks/test_cases |
| Self-hosted ломает миграцию на `auth.users` | Отклонён B; остаёмся на Supabase Auth |
| MCP `supabase` not found сразу после правки json | Namespace появился как `user-supabase` (needsAuth → mcp_auth) |
| Advisors: mutable search_path / SECURITY DEFINER executable | Миграция `harden_auth_triggers` + revoke EXECUTE |
| MCP issue form блокировала агента | Issue #23 через локальный `gh` |
| `app.py` vs пакет `app/` | Entrypoint `wsgi.py` |
| Selenium conftest ломал API pytest | Lazy `importorskip("selenium")` |

### 5.6. Выводы и рекомендации

- API C готов; для учёбы default **Ollama + qwen2.5:7b** (`AI_PROVIDER=ollama`).
- Leopold 72B — переключение env без смены кода.
- Шаг 5: JWT обязателен вне testing; FE Auth опционален только если нет `VITE_SUPABASE_*` (Vitest/mock).

### 5.7. Шаг 5 — безопасность (Auth / RLS / CORS / secrets)

**Промпт:** Senior Backend + security; сначала аудит Supabase → proposal → OK → реализация.

**Результат ([#25](https://github.com/Sintik1/Qa_Asistant/issues/25)):**
- `app/auth.py` + middleware в `app/__init__.py`
- FE: `@supabase/supabase-js`, `/auth`, `RequireAuth`, `apiFetch` с Bearer
- Migration `security_storage_policies` на cloud
- Pytest: `tests/test_auth_jwt.py` + прежние API → **26 passed** (выборка auth/smoke/error/ai)
- Vitest **71**, `npm run build` OK

**Проблемы / решения:**
| Проблема | Решение |
|----------|---------|
| MCP Issue form без Submit | Issue через GitHub REST + `GITHUB_TOKEN` |
| Opaque Bearer без verify | PyJWT HS256 + audience `authenticated` |
| Storage gaps (debug/exports) | доп. policies update/delete |
| Ломать Vitest без env Supabase | `RequireAuth` пропускает, если клиент не сконфигурирован |

---

## 6. Журнал шагов ДЗ

| Шаг ДЗ | Тема | Issue | Статус | Примечание |
|--------|------|-------|--------|------------|
| — | Workflow: backend_documentation + rules | [#19](https://github.com/Sintik1/Qa_Asistant/issues/19) | in progress | каркас; §12 не отменяет §10–11 и остальные rules |
| 1 | Проектирование БД + миграции | [#20](https://github.com/Sintik1/Qa_Asistant/issues/20) | done (awaiting OK) | Variant **B**; `20260928143000_init_variant_b.sql` |
| 2 | Выбор инфраструктуры | [#21](https://github.com/Sintik1/Qa_Asistant/issues/21) | done (awaiting OK) | **A Supabase**; self-hosted отклонён; VPS не нужен |
| 3 | Развертывание БД + MCP | [#22](https://github.com/Sintik1/Qa_Asistant/issues/22) | done (awaiting OK) | project `revyywfeeqdmlgrbakpj`; schema + buckets |
| 4 | API (≥3 CRUD) | [#23](https://github.com/Sintik1/Qa_Asistant/issues/23) | done (awaiting OK) | Hybrid **C**; Ollama 1.5b + Leopold |
| 4b | Тест endpoints + Ollama | [#24](https://github.com/Sintik1/Qa_Asistant/issues/24) | done | Pytest **16/16**; live **17/17** PASS; `docs/API_LIVE_TEST_REPORT.md` |
| 5 | Безопасность (Auth, RLS, CORS) | [#25](https://github.com/Sintik1/Qa_Asistant/issues/25) | done (awaiting OK) | Supabase Auth + JWT middleware + Storage RLS; pytest auth **10**; vitest **71** |
| 6 | Интеграция Frontend | [#26](https://github.com/Sintik1/Qa_Asistant/issues/26) | done (awaiting OK) | **B**: FE `src/api` + hooks; `POST …/generate`; pytest **24**; §4.4 |
| 7 | Ошибки и логирование | — | pending | |
| 8 | Тестирование | — | pending | |
| 9 | Оформление сдачи | — | pending | |

---

_Последнее обновление: 2026-10-03 — шаг 6 вариант B реализован ([#26](https://github.com/Sintik1/Qa_Asistant/issues/26)); коммит после OK._
