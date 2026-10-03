# QA Assistant

Веб-приложение для генерации тест-кейсов из документов требований (PDF / DOCX / DOC / Markdown).

**Стек:** React 19 + TypeScript + Vite + Tailwind · Flask (Python) · Supabase (Auth, Postgres, Storage, RLS) · AI: Ollama / Leopold (Qwen).

**Репозиторий:** https://github.com/Sintik1/Qa_Asistant

| Документ | Назначение |
|----------|------------|
| [`backend_documentation.md`](backend_documentation.md) | **Сдача Backend ДЗ:** архитектура, развёртывание, API, примеры, AI-процесс |
| [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) | Сводный отчёт: API + UI + DB (вердикт PASS) |
| [`development_report.md`](development_report.md) | Журнал стадий + GitHub Issues |
| [`technical_specification.md`](technical_specification.md) | Техническое задание |

---

## Для проверяющего

Публичный cloud-деплой **не обязателен** (критерий ДЗ: «ссылка на деплой **или** инструкции»). Стенд сдачи:

| Слой | Где |
|------|-----|
| БД / Auth / Storage / RLS | **Supabase** (BaaS, Free tier) |
| Backend (Flask) + Frontend (Vite) | **локально** по этому README |
| AI | **Ollama** на машине разработчика или **Leopold** по токену в `.env` |

### Как убедиться, что всё работает

1. **По отчёту (без установки):** [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) — live API **23/23**, UI happy path, запись в Supabase, Pytest. Детали: `docs/API_LIVE_TEST_REPORT.md`, `docs/UI_HAPPY_PATH_REPORT.md`, `docs/DB_PERSISTENCE_TEST_REPORT.md`.
2. **По документации:** [`backend_documentation.md`](backend_documentation.md) — архитектура (§1), развёртывание (§2), API (§3), примеры curl (§4), процесс с AI (§5), журнал шагов 1–9 (§6).
3. **Воспроизвести локально** (ниже «Быстрый старт») → `/auth` → upload → generate → CSV; в Supabase — строки в `documents` / `generation_runs` / `test_cases`.
4. **Автотесты:** `pytest` (backend) и `npm test` (frontend) — см. раздел «Тестирование».

Секреты (`SERVICE_ROLE`, JWT secret, AI token) в git **не** коммитятся — только плейсхолдеры в `.env.example`. Для полного e2e нужны ключи из своего проекта Supabase (или демо у автора на защите / по скринкасту).

**Артефакты сдачи в репо:** код Backend + Frontend, `supabase/migrations/`, `.env.example`, `docker-compose.yml` (UI), `backend_documentation.md`, QA-отчёты.

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
Ожидание: `"status":"ok"`, `"persist":"supabase"` (при настроенных ключах), блок `"ai"`.

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

## Только UI в Docker

Нужен **Docker Desktop**. Полный e2e (Auth + generate + БД) требует отдельно запущенный Flask и ключи Supabase — см. «Быстрый старт».

```bash
docker compose up --build
# http://localhost:8080
docker compose down
```

---

## API (кратко)

Публичные: `GET /api/health`, `POST /api/ai/ping`.  
Остальные `/api/*` — заголовок `Authorization: Bearer <Supabase JWT>`.  
(`AUTH_DEV_BYPASS=1` — **только** локальная отладка, не для проверки безопасности.)

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
