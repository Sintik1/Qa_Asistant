# QA Assistant

Веб-приложение для генерации тест-кейсов из документов требований (PDF / DOCX / DOC / Markdown).

**Стек:** React 19 + TypeScript + Vite + Tailwind · Flask (Python) · Supabase (Auth, Postgres, Storage, RLS) · AI: Ollama / Leopold (Qwen).

Репозиторий: https://github.com/Sintik1/Qa_Asistant

| Документ | Назначение |
|----------|------------|
| [`backend_documentation.md`](backend_documentation.md) | **Сдача Backend ДЗ:** архитектура, деплой, API, примеры запросов |
| [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) | Сводный отчёт тестирования (API + UI + DB) |
| [`development_report.md`](development_report.md) | Журнал стадий разработки + GitHub Issues |
| [`technical_specification.md`](technical_specification.md) | Техническое задание |

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

Нужны: **Node.js 20+**, **Python 3.9+**, аккаунт **Supabase**, опционально **Ollama** (локальный AI).

### 1. Переменные окружения

```bash
cp .env.example .env
cp qa-assistant/.env.example qa-assistant/.env.local
```

В Dashboard Supabase → Settings → API скопируйте URL, `anon` key, `service_role` key, **JWT Secret** в `.env` / `.env.local`.

Важные переменные:

| Переменная | Где | Назначение |
|------------|-----|------------|
| `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` | FE | Auth + клиент |
| `VITE_API_BASE_URL` | FE | Flask (на macOS часто `http://127.0.0.1:5001`) |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_JWT_SECRET` | Flask | JWT + PostgREST |
| `SUPABASE_SERVICE_ROLE_KEY` | Flask only | Storage / admin — **не** во frontend |
| `CORS_ORIGINS` | Flask | whitelist Vite (`localhost` и `127.0.0.1`) |
| `AI_PROVIDER` | Flask | `ollama` (учёба) или `leopold` |

Секреты не коммитить. Полный список — в `.env.example` и `backend_documentation.md` §2.3.

### 2. Backend (Flask)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Опционально: локальный AI на M1 8GB
./scripts/setup_ollama.sh 1.5b
# в отдельном терминале: ollama serve

# Порт 5000 на macOS часто занят AirTunes — используйте 5001
flask --app wsgi run -p 5001
```

Проверка: http://127.0.0.1:5001/api/health

### 3. Frontend (Vite)

```bash
cd qa-assistant
npm install
npm run dev
```

Открыть: **http://127.0.0.1:5173** → `/auth` (регистрация / вход) → загрузка документа → генерация → CSV/DOCX.

---

## Только UI в Docker

Нужен установленный **Docker Desktop**. Flask и Supabase при этом настраиваются отдельно (или UI работает в ограниченном режиме без полного backend).

```bash
docker compose up --build
```

Открыть: **http://localhost:8080**

```bash
docker compose down
```

---

## Что проверить после запуска

1. Зарегистрируйтесь / войдите на `/auth`.
2. **Настройки** — при необходимости отметьте наличие API-токена (`has_api_token`; сам токен Leopold — в server `.env`).
3. На главной загрузите `.md` / `.pdf` / `.docx`.
4. **Генерировать тест-кейсы** → дождитесь таблицы → скачайте CSV или DOCX.
5. Убедитесь, что в Supabase появляются строки в `documents` / `generation_runs` / `test_cases` (при `PERSIST_BACKEND=auto|supabase`).

Негативные сценарии (по имени файла, mock-эвристики UI): `empty`, `fail`, `corrupt`, `slow`.

---

## API (кратко)

Публичные: `GET /api/health`, `POST /api/ai/ping`.  
Остальные `/api/*` — `Authorization: Bearer <Supabase JWT>` (или `AUTH_DEV_BYPASS=1` только для локальной отладки).

| Метод | Path | Назначение |
|-------|------|------------|
| `POST` | `/api/documents/upload` | multipart upload + extract |
| `GET`/`POST` | `/api/documents` | список / создать meta |
| `GET`/`POST`/`DELETE` | `/api/runs`, `/api/runs/<id>` | прогоны |
| `POST` | `/api/runs/<id>/generate` | AI → тест-кейсы |
| `GET` | `/api/runs/<id>/test-cases` | кейсы |
| `PATCH` | `/api/test-cases/<id>` | правка кейса |
| `GET`/`PATCH` | `/api/settings` | chunk-настройки |

Полное описание и curl-примеры: [`backend_documentation.md`](backend_documentation.md) §3–§4.

---

## Тестирование

| Команда / документ | Назначение |
|--------------------|------------|
| `pytest tests/ -q` | Backend unit/API (из корня, с venv) |
| `cd qa-assistant && npm test` | Frontend Vitest |
| `scripts/live_api_full_qa.py` | Live matrix API |
| [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md) | Сводка Full QA |
| [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md) | Адаптив / UI-регресс (исторический) |

```bash
# Backend
source .venv/bin/activate
pytest tests/test_api_smoke.py tests/test_api_error_contract.py tests/test_business_logic_full.py -q

# Frontend
cd qa-assistant && npm test && npm run build
```

UI E2E (Selenium, нужен запущенный app):

```bash
cd tests
QA_ASSISTANT_BASE_URL=http://localhost:5173 pytest -m "ui or security" -v
```

---

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `qa-assistant/` | Frontend (React + Vite + Tailwind) |
| `app/` | Flask HTTP (тонкие routes, auth, CORS) |
| `core/` | Домен / use cases (generate, parse, doc_reader, …) |
| `infrastructure/` | Supabase REST/store, logging, storage |
| `integrations/` | AI client (Ollama / Leopold) |
| `supabase/migrations/` | SQL схема Variant B + RLS |
| `tests/` | Pytest (API) + Selenium |
| `docs/` | QA-отчёты |
| `backend_documentation.md` | Документация Backend ДЗ |
| `docker-compose.yml` | UI-образ на порту 8080 |

Подробнее по frontend: [`qa-assistant/README.md`](qa-assistant/README.md)

---

## Полезные ссылки

- Backend ДЗ (сдача docs): https://github.com/Sintik1/Qa_Asistant/issues/33
- Full QA: https://github.com/Sintik1/Qa_Asistant/issues/29 · https://github.com/Sintik1/Qa_Asistant/issues/32
- DB persistence: https://github.com/Sintik1/Qa_Asistant/issues/31
- UI: `/` — генерация, `/settings` — настройки, `/auth` — вход/регистрация
