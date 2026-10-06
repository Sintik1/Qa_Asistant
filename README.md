# QA Assistant

Веб-приложение для генерации тест-кейсов из документов требований (PDF / DOCX / DOC / Markdown).

**Стек:** React 19 + TypeScript + Vite + Tailwind · Flask (Python) · Supabase (Auth, Postgres, Storage, RLS) · AI: Ollama / Leopold (Qwen).

**Репозиторий:** https://github.com/Sintik1/Qa_Asistant

| Документ | Назначение |
|----------|------------|
| [`backend_documentation.md`](backend_documentation.md) | **Сдача Backend ДЗ:** архитектура, развёртывание, API, примеры, AI-процесс |
| [`cicd_integrations_documentation.md`](cicd_integrations_documentation.md) | **Сдача CI/CD + integrations ДЗ:** пайплайн, security, OAuth, аналитика, мониторинг |
| [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) | Сводный отчёт: API + UI + DB (вердикт PASS) |
| [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md) | Аудит безопасности + remediations |
| [`docs/OAUTH_SETUP.md`](docs/OAUTH_SETUP.md) | OAuth2 Google + Yandex (секреты, redirect, checklist) |
| [`docs/RAG_USAGE.md`](docs/RAG_USAGE.md) | **Как пользоваться RAG:** документы, кейсы, чистка, Table Editor |
| [`development_report.md`](development_report.md) | Журнал стадий + GitHub Issues |
| [`technical_specification.md`](technical_specification.md) | Техническое задание |

---

## Для проверяющего

Публичный cloud-деплой **не обязателен** (критерий ДЗ: «ссылка на деплой **или** инструкции»).  
`docker compose` поднимает **только UI**, не полный стек (см. комментарий в `docker-compose.yml`).

| Слой | Где на стенде сдачи |
|------|---------------------|
| БД / Auth / Storage / RLS | **Supabase** (BaaS, Free tier) |
| Backend (Flask) + Frontend (Vite) | **локально** (или опциональный PaaS — см. ниже) |
| AI | **Ollama** локально или **Leopold** по токену в server `.env` |

### Демо-вход (Supabase Auth)

| Поле | Значение |
|------|----------|
| URL UI | `http://127.0.0.1:5173/auth` (после «Быстрый старт») |
| Email | `demo.reviewer@qatest.local` |
| Password | `DemoReviewer-2026!` |

Учётка подтверждена (`email_confirmed`). После входа открываются Home / Settings (с вкладками).  
Не используйте `AUTH_DEV_BYPASS` для проверки Auth — только реальный login.

### Чеклист happy path + Table Editor

После входа демо-учёткой:

1. Главная → загрузить небольшой `.md` с требованиями (например `tests/fixtures/live_qa/login_requirements.md`).
2. Нажать **Генерировать тест-кейсы** → дождаться таблицы кейсов → **Скачать CSV**.
3. Supabase Dashboard → **Table Editor** (проект автора или свой с теми же миграциями) — для `user_id` демо-пользователя должно появиться:

| Таблица | Что ожидать после одного generate |
|--------|-----------------------------------|
| `profiles` | 1 строка на пользователя (создаётся signup-триггером) |
| `user_settings` | 1 строка (chunk defaults) |
| `documents` | **+1** строка: `original_filename`, `status` ≈ `parsed`/`extracted`, `storage_path` |
| `generation_runs` | **+1** строка: `document_id`, `status` завершённого прогона, `case_count` ≥ 1 |
| `test_cases` | **≥1** строк с `run_id`, полями `name` / `status` / `step` / `expected_result` |
| `generation_chunks` | 0+ (зависит от чанкинга; для короткого md часто 0–N) |

Фильтр в Table Editor: колонка `user_id` = id пользователя `demo.reviewer@qatest.local` (Authentication → Users).

### Как ещё убедиться без своего стенда

1. **Отчёт:** [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) — API 23/23, UI, DB PASS.  
2. **Документация:** [`backend_documentation.md`](backend_documentation.md) §1–§5.  
3. **Скринкаст happy path (в репо):**  
   - видео: [`docs/screencast/happy_path.mp4`](docs/screencast/happy_path.mp4)  
   - GIF: [`docs/screencast/happy_path.gif`](docs/screencast/happy_path.gif)  
   - кадры: [`docs/screencast/frames/`](docs/screencast/frames/) · описание: [`docs/screencast/README.md`](docs/screencast/README.md)  
   Сценарий: демо-вход → upload `login_requirements.md` → generate → таблица + «Скачать CSV».  
4. **Опциональный бесплатный деплой:** Frontend → Vercel / Cloudflare Pages; Flask → Railway / Render. В env PaaS: **не** ставить `AUTH_DEV_BYPASS`; задать `PUBLIC_DEPLOY=1` или `FLASK_ENV=production`, `CORS_ORIGINS` = URL фронта, `VITE_API_BASE_URL` = URL API. Демо-вход тот же (Supabase общий).

### AUTH_DEV_BYPASS (обязательно вне публичных окружений)

- Флаг **только** для локальной отладки на ноутбуке (`# AUTH_DEV_BYPASS=1` в `.env`, закомментирован по умолчанию).  
- В коде **игнорируется**, если `FLASK_ENV|ENV|APP_ENV=production`, `PUBLIC_DEPLOY=1`, или есть маркеры Railway/Render/Fly/Vercel/Heroku.  
- На проверке Auth / e2e используйте **демо-вход** выше, не bypass.

Секреты (`SERVICE_ROLE`, JWT secret, AI token) в git **не** коммитятся.

**Артефакты в репо:** Backend + Frontend, `supabase/migrations/`, `.env.example`, `docker-compose.yml` (**только UI**), `backend_documentation.md`, QA-отчёты.

---

## Архитектура (кратко)

```text
React (Vite) ──JWT──► Supabase Auth / PostgREST / Storage
       │
       └──HTTP──► Flask (upload / generate / AI) ──► Supabase (RLS / Storage)
                         └──► Ollama или Leopold
```

Подробности: [`backend_documentation.md`](backend_documentation.md) §1–§3.

---

## Быстрый старт (полный стек)

Нужны: **Node.js 20+**, **Python 3.9+**, аккаунт **[Supabase](https://supabase.com)** (Free), для генерации кейсов — **Ollama** или токен Leopold.

### 1. Переменные окружения

```bash
cp .env.example .env
cp qa-assistant/.env.example qa-assistant/.env.local
```

В Supabase Dashboard → **Settings → API** скопируйте URL, `anon` key, `service_role` key, **JWT Secret** в `.env` и `qa-assistant/.env.local`.

| Переменная | Где | Назначение |
|------------|-----|------------|
| `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` | FE | Auth + клиент |
| `VITE_API_BASE_URL` | FE | Flask (на macOS часто `http://127.0.0.1:5001`) |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_JWT_SECRET` | Flask | JWT + PostgREST |
| `SUPABASE_SERVICE_ROLE_KEY` | Flask only | Storage / admin — **никогда** во frontend |
| `CORS_ORIGINS` | Flask | whitelist Vite (`localhost` и `127.0.0.1`) |
| `AI_PROVIDER` | Flask | `ollama` (учёба) или `leopold` |
| `PERSIST_BACKEND` | Flask | `auto` или `supabase` для записи в БД |

Полный список — в `.env.example` и `backend_documentation.md` §2.3.

Миграции схемы (если поднимаете **свой** проект Supabase): SQL из `supabase/migrations/` через SQL Editor или CLI. В учебном проекте автора схема уже применена на cloud Supabase.

### 2. Backend (Flask)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Локальный AI (MacBook Air M1 8GB → модель 1.5b)
./scripts/setup_ollama.sh 1.5b
# в отдельном терминале:
ollama serve

# Порт 5000 на macOS часто занят AirTunes — используйте 5001
flask --app wsgi run -p 5001
```

Проверка: http://127.0.0.1:5001/api/health  
Ожидание: `"status":"ok"`, `"api":"qa-assistant"`, `"persist":"supabase"` (при настроенных ключах), блоки `"ai"` и `"checks"`.  
Мониторинг: [`docs/UPTIME_SETUP.md`](docs/UPTIME_SETUP.md) (UptimeRobot + `scripts/watch_health.py`).  
Логирование: [`docs/LOGGING.md`](docs/LOGGING.md) (JSON + AI scenarios `tools/analyze_logs.py`).  
Интеграции QA (шаг 8): [`docs/INTEGRATIONS_QA_STEP8.md`](docs/INTEGRATIONS_QA_STEP8.md).

### 3. Frontend (Vite)

```bash
cd qa-assistant
npm install
npm run dev
```

Открыть: **http://127.0.0.1:5173**

1. `/auth` — регистрация / вход (Supabase Auth).  
2. Главная — загрузить `.md` / `.pdf` / `.docx`.  
3. **Генерировать тест-кейсы** → таблица → скачать CSV / DOCX.  
4. (Опционально) Dashboard Supabase → Table Editor: есть строки после генерации.

---

## Docker: только UI (не полный стек)

`docker-compose.yml` **намеренно** поднимает один сервис — статическую сборку React (nginx :8080).  
**Не** включает Postgres, Flask, Ollama, Supabase.

Полный e2e: «Быстрый старт» (Flask + Vite + Supabase + AI). Docker UI полезен для проверки вёрстки; API всё равно нужен отдельно (`VITE_API_BASE_URL`).

```bash
docker compose up --build
# http://localhost:8080  — только frontend
docker compose down
```

---

## API (кратко)

Публичные: `GET /api/health`, `POST /api/ai/ping`.  
Остальные `/api/*` — заголовок `Authorization: Bearer <Supabase JWT>`.

| Метод | Path | Назначение |
|-------|------|------------|
| `POST` | `/api/documents/upload` | multipart upload + extract |
| `GET`/`POST` | `/api/documents` | список / meta |
| `GET`/`POST`/`DELETE` | `/api/runs`, `/api/runs/<id>` | прогоны |
| `POST` | `/api/runs/<id>/generate` | AI → тест-кейсы |
| `GET` | `/api/runs/<id>/test-cases` | кейсы |
| `PATCH` | `/api/test-cases/<id>` | правка кейса |
| `GET`/`PATCH` | `/api/settings` | chunk-настройки |

Примеры curl: [`backend_documentation.md`](backend_documentation.md) §4.

---

## Тестирование

| Команда / документ | Назначение |
|--------------------|------------|
| [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) | Сводка Full QA (основной отчёт для сдачи) |
| `pytest tests/…` | Backend unit/API |
| `cd qa-assistant && npm test` | Frontend Vitest |
| `scripts/live_api_full_qa.py` | Live matrix API (нужен запущенный Flask) |

```bash
source .venv/bin/activate
pytest tests/test_api_smoke.py tests/test_api_error_contract.py tests/test_business_logic_full.py -q

cd qa-assistant && npm test && npm run build
```

### CI (GitHub Actions)

На каждый push/PR в `main`/`master`: lint → test → build (frontend + backend) + **npm audit** / **pip-audit**. Auto-deploy **выключен** (локальный Flask/Ollama) — см. [`cicd_integrations_documentation.md`](cicd_integrations_documentation.md) §2 · Issue [#38](https://github.com/Sintik1/Qa_Asistant/issues/38).

Локально повторить CI: §2.3 в том же документе.

### Security

Аудит и remediations: [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md) · Issue [#39](https://github.com/Sintik1/Qa_Asistant/issues/39).

| Мера | Где |
|------|-----|
| JWT + RLS; `AUTH_DEV_BYPASS` hard-disable на PaaS | Flask / Supabase |
| Security headers (`nosniff`, `DENY` frame, Referrer-Policy) | Flask `after_request` |
| Admin log analysis | `LOG_ANALYZE_ADMIN_TOKEN` + `X-Admin-Token` (обязателен вне tests) |
| AI token | только server `.env`; UI не пишет секреты в `localStorage` |
| Deps | `npm audit` / `pip-audit` в CI |

---

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `qa-assistant/` | Frontend (React + Vite + Tailwind) |
| `app/` | Flask HTTP (routes, auth, CORS) |
| `core/` | Use cases (generate, parse, doc_reader, …) |
| `infrastructure/` | Supabase REST/store, logging, storage |
| `integrations/` | AI client (Ollama / Leopold) |
| `supabase/migrations/` | SQL схема Variant B + RLS |
| `tests/` | Pytest + Selenium |
| `.github/workflows/` | GitHub Actions (`ci.yml`) |
| `docs/` | QA-отчёты |
| `backend_documentation.md` | Документация Backend ДЗ |
| `docker-compose.yml` | UI-образ на порту 8080 |

Frontend-only заметки: [`qa-assistant/README.md`](qa-assistant/README.md)

---

## Issues / журнал

- Сдача docs (шаг 9): https://github.com/Sintik1/Qa_Asistant/issues/33  
- Full QA: https://github.com/Sintik1/Qa_Asistant/issues/29 · https://github.com/Sintik1/Qa_Asistant/issues/32  
- DB persistence: https://github.com/Sintik1/Qa_Asistant/issues/31  

UI: `/` — генерация, `/settings` — настройки, `/auth` — вход / регистрация.
