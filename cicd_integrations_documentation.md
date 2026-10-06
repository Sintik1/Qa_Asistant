# CI/CD & Integrations Documentation — QA Assistant

Документ — **артефакт сдачи** домашнего задания «Настройка CI/CD и интеграция сервисов» и живой журнал работ по шагам 1–9.

Репозиторий: https://github.com/Sintik1/Qa_Asistant  
Эпик: [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
**Файлы сдачи (формат ДЗ):** [`integration_documentation.md`](integration_documentation.md) · [`security_audit.md`](security_audit.md)  
Связанные артефакты: [`backend_documentation.md`](backend_documentation.md) · [`development_report.md`](development_report.md) · [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md)

**Стек приложения (база):** React (Vite) + Flask + Supabase Auth/Postgres/Storage + Ollama/Leopold.

### Итог сдачи (шаги 1–9)

| Шаг | Результат | Статус |
|-----|-----------|--------|
| 0 | Каркас документа + план + уточнения | **done (awaiting OK)** — все G1–G9 locked |
| 1 | CI/CD пайплайн | **done (awaiting OK)** — [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) |
| 2 | Аудит безопасности | **done (awaiting OK)** — remediations applied [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) |
| 3 | OAuth2 (Google + Yandex) | **done (awaiting OK)** — [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) |
| 4 | Аналитика (Яндекс.Метрика) | **done (awaiting OK)** — [#41](https://github.com/Sintik1/Qa_Asistant/issues/41) |
| 5 | Платежи (опционально) | **skipped** (G7) |
| 6 | Мониторинг (UptimeRobot) | **done (awaiting OK)** — tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |
| 7 | Логирование | **done (awaiting OK)** — tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |
| 8 | Тестирование и оптимизация | **done (awaiting OK)** — tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |
| 9 | Оформление + README | **done (awaiting OK)** — tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |

> Решения по платформам (CI, хостинг, OAuth-провайдер, аналитика, платежи) фиксируются после согласования с пользователем — см. §0 и §6.

---

## Содержание

0. [Уточнения и gate-решения](#0-уточнения-и-gate-решения)
1. [Описание архитектуры интеграций](#1-описание-архитектуры-интеграций)
2. [CI/CD](#2-cicd)
3. [Безопасность](#3-безопасность)
4. [OAuth2](#4-oauth2)
5. [Аналитика](#5-аналитика)
6. [Платежи (опционально)](#6-платежи-опционально)
7. [Мониторинг и Health Check](#7-мониторинг-и-health-check)
8. [Логирование](#8-логирование)
9. [Процесс разработки с AI](#9-процесс-разработки-с-ai)
10. [Журнал шагов ДЗ](#10-журнал-шагов-дз)

---

## 0. Уточнения и gate-решения

Перед реализацией шагов 1–9 нужны ответы пользователя (зафиксировать здесь после выбора).

| # | Вопрос | Варианты / рекомендация | Решение |
|---|--------|-------------------------|---------|
| G1 | Платформа CI/CD | **A GitHub Actions** | ✅ **A** |
| G2 | Что деплоить автоматически | CI + FE Pages | ✅ **B** — lint/test/build + **auto-deploy Frontend** на GitHub Pages; Flask/AI локально |
| G3 | Хостинг frontend | GitHub Pages | ✅ **GitHub Pages** https://sintik1.github.io/Qa_Asistant/ |
| G4 | Хостинг backend (Flask) + AI | нет бюджета на cloud AI | ✅ **только локально** (Flask + Ollama); Supabase уже Free cloud |
| G5 | OAuth2 провайдер | Google + Yandex через Supabase | ✅ **C** оба |
| G6 | Аналитика | Яндекс.Метрика | ✅ **A** |
| G7 | Платежи (шаг 5) | опционально | ✅ **пропускаем** |
| G8 | Мониторинг | UptimeRobot free | ✅ **A** (пинг `/api/health` когда URL доступен) |
| G9 | MCP | по необходимости агента | ✅ агент решает; сначала без новых MCP |

### 0.1. Разница G2 (что происходит при push в `main`)

| Вариант | Что делает пайплайн | Деньги / аккаунты | Работает ли AI с публичного UI? | Кому подходит |
|---------|---------------------|-------------------|----------------------------------|---------------|
| **A** FE+BE auto-deploy | После тестов деплоит **и** React, **и** Flask на PaaS | Нужны аккаунты Vercel+Railway (и т.п.); free tier часто есть, но **Ollama/тяжёлый AI на free PaaS почти нереально** | Только если AI = Leopold по API-токену (облако), не локальный Ollama | Команда с бюджетом/токеном Leopold 24/7 |
| **B** только FE | Деплоит **только** статику React (Vercel и т.п.). Flask остаётся у тебя на ноутбуке | Бесплатно (Vercel free) | **Нет** для проверяющего из интернета: UI на Vercel не достучится до `127.0.0.1:5001`. Можно смотреть вёрстку/Auth (Supabase), generate — нет | Когда нужен «публичный URL UI» для галочки, API локально |
| **C** только CI | `lint → test → build`, **без** автодеплоя. В docs — инструкция локального стенда (+ скринкаст как раньше) | **0 ₽**, только GitHub | Как сейчас: полный стек локально | **Твой случай (G4): нет бюджета на cloud AI** |

**Рекомендация при твоих ограничениях: G2 = C.**

Как закрыть формулировку ДЗ «настроить автодеплой»:
- в workflow сделать job `deploy` с `if: false` **или** отдельный manual `workflow_dispatch` «Deploy docs only»;
- в `cicd_integrations_documentation.md` явно: auto-deploy отключён из‑за локального AI; при появлении бюджета — включить B (FE) или A (FE+BE+Leopold).
- критерий сдачи у вас уже допускал «ссылка **или** инструкции» ([#34](https://github.com/Sintik1/Qa_Asistant/issues/34)).

Альтернатива «чуть больше галочек без бюджета»: **G2 = B** (бесплатный Vercel только UI) + в README крупно: «API/AI только локально». Полный happy path для проверяющего — всё равно локальный стенд/скринкаст.

### 0.2. Разница G3 (куда выкладывать Frontend)

Все три — **бесплатные static hosts** под Vite/React. Разница в удобстве, не в цене.

| Хостинг | Плюсы | Минусы | Для нас |
|---------|-------|--------|---------|
| **Vercel** | Лучшая связка с GitHub/Vite, env в UI, preview на PR | Аккаунт Vercel | **Рекомендация**, если выберешь G2=B |
| **Netlify** | То же по сути, forms/plugins | Чуть другой DX | Ок, если уже есть аккаунт |
| **Cloudflare Pages** | Сильный CDN, generous free | Иногда дольше настройка build | Ок как план B |

При **G2 = C** хостинг FE **не нужен** → G3 = N/A.

### 0.3. Как это стыкуется с уже имеющимся

```text
Сейчас (и при G2=C):
  GitHub Actions: lint/test/build ✅
  Supabase Free: Auth/DB/Storage ✅ (уже)
  Ноутбук: Flask + Ollama + Vite ✅
  UptimeRobot: имеет смысл, когда появится публичный URL health;
              при только-локальном API — мониторим после optional tunnel/PaaS
              или документируем «ready when PUBLIC_API_URL set»
```

### Что уже есть в проекте (не дублировать с нуля)

| Область | Факт |
|---------|------|
| Auth | Supabase email/password + JWT middleware Flask (`app/auth.py`) |
| Health | `GET /api/health` (persist, AI, RAG) |
| Логи | JSON lines: `infrastructure/logging_setup.py` (Backend ДЗ шаг 7) |
| CORS / secrets | whitelist + `.env` / `.env.example` |
| CI | **нет** `.github/workflows/` — шаг 1 создаёт с нуля |
| Публичный деплой | ранее опционален для проверяющего ([#34](https://github.com/Sintik1/Qa_Asistant/issues/34), [#35](https://github.com/Sintik1/Qa_Asistant/issues/35)) |

---

## 1. Описание архитектуры интеграций

### 1.1. Целевая схема (после ДЗ)

```text
                    GitHub Actions (CI)
                    lint → test → build → [deploy]
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
┌─────────┐         ┌────────────┐         ┌──────────┐
│ FE host │         │ Flask PaaS │         │ Supabase │
│(Vercel?)│────────►│ (Railway?) │────────►│ Auth+DB  │
└────┬────┘         └─────┬──────┘         └────┬─────┘
     │                    │                     │
     │ analytics          │ health/logs         │ OAuth providers
     ▼                    ▼                     ▼
  Метрика/GA          Uptime / logs        Google / Yandex
```

### 1.2. Принципы

- Секреты только в GitHub Secrets / PaaS env / `.env` (не в git).
- Тонкий HTTP-слой Flask; OAuth через Supabase Auth Client на FE + JWT на BE (как сейчас).
- CI обязан гонять Pytest (backend) и Vitest/lint (frontend) на PR и на `main`.
- Деплой на `main`/`master` — только после зелёных checks (если выбран auto-deploy).

---

## 2. CI/CD

Issue: [#38](https://github.com/Sintik1/Qa_Asistant/issues/38)

### 2.1. Выбор платформы

**GitHub Actions** (G1=A). Файл: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

Согласовано на шаге 1:
- **Deploy job** — отдельный stage с `if: false` (виден в Actions, но не выполняется; G2=C).
- **Python quality** — Ruff lint + `ruff format --check` ([`pyproject.toml`](pyproject.toml)).
- **Триггеры** — `push`/`pull_request` на `main` и `master`, плюс `workflow_dispatch`.

### 2.2. Workflow stages (факт)

| Job | Stage | Команды |
|-----|-------|---------|
| `frontend` | install | `npm ci` (Node 22, cache) |
| | lint | `npm run lint` (oxlint) |
| | test | `npm run test` (Vitest) |
| | build | `npm run build` (`tsc -b` + Vite) |
| `backend` | install | `pip install -r requirements.txt` + `ruff` |
| | lint | `ruff check app core infrastructure integrations wsgi.py` |
| | format | `ruff format --check …` |
| | test | `pytest tests/ -m "not ui and not security"` + `--ignore` ui/security modules (no Selenium in CI) |
| `deploy` | deploy | **GitHub Pages** (push to main) — см. §2.4 |

**CI env (backend):** `FLASK_ENV=testing`, `PERSIST_BACKEND=memory`, `EMBEDDING_PROVIDER=hash`, `AI_PROVIDER=ollama`.

**Вне CI:** Selenium `@pytest.mark.ui` и `@pytest.mark.security` (нужны Chrome + dev-сервер) — локально / отдельный job позже.

### 2.3. Локальный прогон (как в Actions)

```bash
# Frontend
cd qa-assistant && npm ci && npm run lint && npm run test && npm run build

# Backend
pip install -r requirements.txt ruff
ruff check app core infrastructure integrations wsgi.py
ruff format --check app core infrastructure integrations wsgi.py
python -m pytest tests/ -m "not ui and not security" -q
```

Опционально: `pip install -r requirements-dev.txt` (Ruff + deps).

### 2.4. Автодеплой

**Включён для Frontend (G2=B).** Job `deploy` после зелёных `frontend`+`backend` пушит Vite build на **GitHub Pages**.

- URL: https://sintik1.github.io/Qa_Asistant/
- Monitor: https://sintik1.github.io/Qa_Asistant/status.json
- Инструкция one-time Pages source: [`docs/DEPLOY_GITHUB_PAGES.md`](docs/DEPLOY_GITHUB_PAGES.md)
- Flask + Ollama **не** деплоятся в облако (G4); полный generate — локально.

**Проверка пайплайна:** после `git push` в GitHub → вкладка **Actions** → workflow **CI**. Локально перед push: команды из §2.3 (на момент реализации: **99** pytest, **78** vitest).

### 2.5. AI-генерация базового пайплайна

Базовый YAML сгенерирован агентом по gate G1/G2 и структуре монорепо; доработки: исключение Selenium-тестов, Ruff scope, TS-fix для green `npm run build`.

---

## 3. Безопасность

Issue: [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) · **Файл сдачи:** [`security_audit.md`](security_audit.md) · Журнал: [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md)

### 3.1. Dependency audit (2026-10-05)

| Tool | Результат |
|------|-----------|
| `npm audit` (qa-assistant) | **0** vulnerabilities |
| `pip-audit -r requirements.txt` | **8** advisories / **5** packages |
| `safety` | не использован (interactive login) |

Ключевые backend: **flask-cors 5.0.1 → ≥6.0.0** (High); python-dotenv → 1.2.2; pytest → 9.0.3; transitive click/anyio.

### 3.2. OWASP Top 10 (итог аудита)

| Риск | Состояние | Действие |
|------|-----------|----------|
| Injection (SQL) | PostgREST / нет string-SQL | OK |
| XSS | React text; нет `dangerouslySetInnerHTML` | OK |
| CSRF | Bearer JWT | OK (низкий classic CSRF) |
| Broken Access | JWT + bypass hard-disable на PaaS | OK + усилить admin analyze-logs |
| Sensitive data | `.env` / не коммитить | OK; legacy localStorage token — cleanup |
| Misconfig | CORS whitelist; **нет security headers** | добавить headers |
| Vulnerable deps | flask-cors и др. | обновить после gate |
| Logging | JSON + analyze-logs | ужесточить admin token |

### 3.3. Найденные проблемы и исправления

| ID | Severity | Находка | Исправление |
|----|----------|---------|-------------|
| D1 | High | flask-cors 5.0.1 (3 CVE) | ✅ `flask-cors>=6.0,<7` |
| D2 | Low–Med | dotenv / pytest / click / anyio | ✅ pins с markers (≥3.10 = fixed; CI Python **3.11**) |
| C1 | Medium | нет security headers | ✅ B1a в `app/__init__.py` |
| C2 | Medium | analyze-logs без обязательного admin token | ✅ B2a — token required вне `TESTING` |
| C3 | Low | Settings писал token в localStorage | ✅ B3a — только `has_api_token` + purge legacy key |
| C4 | Low | нет audit в CI | ✅ C1 — `npm audit` + `pip-audit` в `ci.yml` |
| — | — | README Security | ✅ C2 |

Полный отчёт: [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md). Gate: **A2+B1a+B2a+B3a+B4b+B5b+C1+C2**.

---

## 4. OAuth2

Issue: [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) · Гайд: [`docs/OAUTH_SETUP.md`](docs/OAUTH_SETUP.md)

### 4.1. Провайдер (G5=C)

| Провайдер | Реализация |
|-----------|------------|
| Google | **Supabase Auth Provider** — FE `signInWithOAuth({ provider: 'google' })` → `…/auth/v1/callback` |
| Yandex | Flask Authorization Code (`/api/auth/oauth/yandex/*`) → Supabase Admin session |

Legacy Flask Google routes (`/api/auth/oauth/google/*`) остаются опционально.

### 4.2. Backend

- Публичные: `GET /api/auth/oauth/status` (`google.flow=supabase_auth_provider`), Yandex start/callback
- `GET /api/auth/me` — user_id/email из JWT (email/Google/Yandex)
- Секреты: Google Client Secret → **Supabase Dashboard**; Yandex + `SUPABASE_SERVICE_ROLE_KEY` → `.env`

### 4.3. Frontend

- `/auth` — Google (Supabase) / Yandex (Flask)
- `/auth/callback` — PKCE session (Google) + hash tokens (Yandex)

### 4.4. Тесты

| Проверка | Результат |
|----------|-----------|
| Pytest `tests/test_oauth.py` | **PASS** (status + Yandex + legacy Google start) |
| Vitest `AuthPage.test.tsx` | **PASS** |
| Live Google | после Enable Google в Dashboard + redirect URI Supabase callback (см. OAUTH_SETUP) |
---

## 5. Аналитика

**Статус:** done (awaiting OK) — [#41](https://github.com/Sintik1/Qa_Asistant/issues/41).  
Инструкция: [`docs/METRIKA_SETUP.md`](docs/METRIKA_SETUP.md).

### 5.1. Сервис

**Яндекс.Метрика** (G6 = A).

- Публичный counter id: `VITE_YANDEX_METRIKA_ID` (Vite FE).
- Без id → no-op (CI / локально без счётчика).
- Скрипт: `https://mc.yandex.ru/metrika/tag.js`.
- SPA: `ym(id, 'hit', path)` на смене React Router (`MetrikaRouteTracker`).
- Цели: `ym(id, 'reachGoal', name[, params])`.
- Webvisor **выключен** по умолчанию (меньше PII в сессиях).

### 5.2. События

| Событие | Когда | Где |
|---------|-------|-----|
| `hit` (page_view) | смена роута | `MetrikaRouteTracker` |
| `auth_login` | успешный login / OAuth callback | `AuthPage`, `AuthCallbackPage` |
| `auth_signup` | успешная регистрация | `AuthPage` |
| `auth_oauth_start` | клик Google/Yandex | `AuthPage` |
| `document_upload` | успешный `uploadDocument` | `useTestCaseGeneration` |
| `generate_start` / `generate_success` / `generate_error` | пайплайн генерации | `useTestCaseGeneration` |
| `csv_download` | экспорт CSV | `useTestCaseGeneration` |
| `chat_send` | отправка RAG-вопроса | `ChatPage` |

### 5.3. Код

| Файл | Назначение |
|------|------------|
| `qa-assistant/src/analytics/metrika.ts` | init / hit / reachGoal |
| `qa-assistant/src/analytics/MetrikaRouteTracker.tsx` | SPA hits |
| `qa-assistant/src/analytics/metrika.test.ts` | Vitest |

### 5.4. Env

```env
VITE_YANDEX_METRIKA_ID=113444012
```

Только public id (счётчик ДЗ: `113444012`). Секреты Metrika API (если понадобятся отчёты с сервера) — только в `.env`, не в `VITE_*`.

---

## 6. Платежи (опционально)

> Gate G7. Если **A — пропустить**, раздел остаётся с обоснованием «out of scope продукта / опционально по ТЗ ДЗ».

### 6.1. Сервис

_TBD._

### 6.2. Backend / webhook / FE UI

_TBD при выборе B/C._

---

## 7. Мониторинг и Health Check

**Статус:** in progress — [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) (шаг 6; отдельная Issue-форма MCP недоступна в UI).  
Инструкция: [`docs/UPTIME_SETUP.md`](docs/UPTIME_SETUP.md).

### 7.1. Endpoint

`GET /api/health` — публичный (без JWT). HTTP **200**, пока процесс жив.

Payload (`core/health.py`):

| Поле | Смысл |
|------|--------|
| `status` | `ok` / `degraded` / `fail` |
| `api` | всегда `qa-assistant` (keyword для UptimeRobot) |
| `checks.app` | процесс |
| `checks.disk` | free space на `uploads/` |
| `checks.db` | soft ping PostgREST (если `persist=supabase`) |
| `checks.ai` | configured provider/model |

### 7.2. UptimeRobot (G8=A)

При публичном URL: HTTP(s) monitor → `/api/health`, keyword `qa-assistant`, alert email.  
Пока G2=C (localhost) — внешний монитор не видит API; использовать локальный watcher.

### 7.3. Локальный watcher

```bash
python scripts/watch_health.py
INTERVAL_SEC=30 WATCH_LOOPS=0 python scripts/watch_health.py
```

### 7.4. Тесты

`tests/test_health_monitoring.py` — контракт `checks` + keyword.

---

## 8. Логирование

> База: Backend ДЗ шаг 7. **CI/CD ДЗ шаг 7** — scenarios AI-анализа, redact секретов, поля `service`/`env`/`event`, локальная централизация (G2=C). Полный гайд: [`docs/LOGGING.md`](docs/LOGGING.md).

### 8.1. Формат и destination

- JSON lines: `infrastructure/logging_setup.py` → stdout + rotating `logs/app.log`
- Поля: `ts`, `level`, `logger`, `service` (`LOG_SERVICE`), `env` (`APP_ENV`), `event`, `msg`, `request_id`, HTTP context
- Env: `LOG_LEVEL`, `LOG_JSON`, `LOG_TO_FILE`, `LOG_DIR`, `LOG_FILE`, `LOG_SERVICE`, `APP_ENV`, …

### 8.2. AI-анализ (сценарии)

| Scenario | Фокус |
|----------|--------|
| `general` | triage top errors |
| `auth` | 401/403 / JWT / OAuth |
| `cors` | CORS / Origin |
| `ai` | Ollama / timeouts |
| `persist` | Supabase / RLS |

- CLI: `python tools/analyze_logs.py --scenario auth --file tests/fixtures/logs/auth_401.jsonl`
- API: `POST /api/admin/analyze-logs` + `{"scenario":"auth",…}` (admin token вне tests)
- Перед моделью: `redact_secrets` (Bearer JWT, `sb_secret_*`, api keys)

### 8.3. Централизация (G2=C)

Без cloud drain: файл на машине Flask. Опционально позже Vector/Promtail. Supabase Dashboard Logs — paste в `--stdin`.

### 8.4. Тесты / фикстуры

- `tests/test_logging_and_errors.py` — formatter, redact, scenarios, admin gate, error contracts
- `tests/fixtures/logs/{auth_401,cors_noise,ai_timeout}.jsonl`

---

## 9. Процесс разработки с AI

### 9.1. Workflow стадии

Как в Backend ДЗ: отдельный промпт на шаг → Issue → код/конфиг → тесты → обновление этого файла + `development_report.md` → gate OK пользователя.

### 9.2. Техники (накопительно)

| Техника | Когда |
|---------|--------|
| Уточнения + gate до кода | Шаг 0 (этот документ) |
| Генерация CI YAML через AI + ручной review secrets | Шаг 1 |
| AI security review + `npm audit` / pip-audit | Шаг 2 |
| SPA analytics wrapper + Vitest no-op without id | Шаг 4 (Метрика) |
| Health checks + local watcher (G2=C) | Шаг 6 (UptimeRobot) |
| Scenario prompts ×3 + redact before AI | Шаг 7 (логирование) |
| Integrations QA + apply AI perf fixes | Шаг 8 |
| Submission docs (`integration_documentation.md`, `security_audit.md`) | Шаг 9 |

### 9.3. Примеры промптов и результатов

#### Промпт: one-time Pages setup (agent)

**Запрос:** «Сделай один раз вручную (иначе deploy упадёт) — сделай сам».

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- Settings → Pages → Source **GitHub Actions**
- Repo Variables: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- Unblock CI: `overrides.source-map-js=1.2.2` (CVE-2026-93749 / GHSA-68fv-2mgg-jv7q)

#### Промпт: Google OAuth через Supabase

**Запрос:** вернуться к OAuth через Supabase; пользователь авторизовался в GitHub / «подтверждаю».

**Результат (tracked [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)):**
- FE Google → `supabase.auth.signInWithOAuth`; Yandex Flask
- Dashboard: Google Enabled, Redirect URLs×3, Site URL local Vite
- Осталось: Google Console redirect = Supabase `/auth/v1/callback`

#### Промпт: шаг 9 — оформление результатов

**Запрос:** документация CI/CD / интеграции / security / мониторинг+логи; обновить README; сверить формат сдачи п.1–4.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- [`integration_documentation.md`](integration_documentation.md) — артефакт сдачи + чеклист §0
- [`security_audit.md`](security_audit.md) — уязвимости / фиксы / рекомендации
- README: блок «Сдача CI/CD ДЗ»; G2=C = инструкции + screencast

#### Промпт: шаг 8 — тестирование и оптимизация

**Запрос:** Senior QA; проверить OAuth2 / аналитику / платежи / CI; AI-оптимизация; исправить баги.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- Отчёт [`docs/INTEGRATIONS_QA_STEP8.md`](docs/INTEGRATIONS_QA_STEP8.md)
- Pytest **114** / Vitest **85**; Yandex OAuth + Metrika live PASS
- Google live: `redirect_uri_mismatch` (config Console) — `docs/OAUTH_SETUP.md` §4.1
- Fixes: hermetic bypass tests, `UPLOADS_DIR`, PostgREST→503, FE code-split
- Платежи N/A (G7)

#### Промпт: шаг 7 — логирование

**Запрос:** роль Senior Backend; JSON + централизация; промпты×3; после согласования выполнить. Пользователь: «ок».

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- `SCENARIO_PROMPTS` (general/auth/cors/ai/persist) + `redact_secrets`
- JSON поля `service`/`env`/`event`; CLI `--scenario` / `--list-scenarios`
- Fixtures + Pytest; `docs/LOGGING.md`

#### Промпт: шаг 6 — мониторинг

**Запрос:** подтверждаю / переходим дальше (после Метрики).

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- `core/health.py` + `checks` в `GET /api/health`
- `docs/UPTIME_SETUP.md`, `scripts/watch_health.py`
- Pytest `tests/test_health_monitoring.py`
- MCP Create Issue UI недоступен у пользователя → трекинг в эпике #37

#### Промпт: шаг 4 — Яндекс.Метрика

**Запрос:** делать по ДЗ, использовать Яндекс.Метрику.

**Результат ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)):**
- `src/analytics/metrika.ts` + `MetrikaRouteTracker` + goals на Auth/upload/generate/CSV/chat
- `VITE_YANDEX_METRIKA_ID`, `docs/METRIKA_SETUP.md`
- Vitest: disabled without id; init + reachGoal when set

#### Промпт: шаг 1 — CI/CD пайплайн

**Запрос:** Senior fullstack; GitHub Actions; install/build/test/lint/deploy; согласование с G2=C; затем реализация.

**Согласовано:** deploy job `if: false`; Ruff; триггеры PR+main.

**Результат ([#38](https://github.com/Sintik1/Qa_Asistant/issues/38)):**
- `.github/workflows/ci.yml`, `pyproject.toml`, `requirements-dev.txt`
- Ruff auto-fix/format на `app/`/`core/`/`infrastructure/`/`integrations/`
- FE: type fixes для green `npm run build`

#### Промпт: план CI/CD ДЗ + отдельный артефакт документации

**Запрос:** рассуждать пошагово; уточнить; создать файл по аналогии с `backend_documentation.md`; фиксировать также в Issues / `development_report.md`; план; MCP только по согласованию.

**Результат:** Issue [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); создан `cicd_integrations_documentation.md`; план шагов 0–9; список уточнений G1–G9.

### 9.4. Проблемы и решения

| Проблема | Решение |
|----------|---------|
| Публичный деплой vs критерий «или инструкции» | Gate G2: можно CI-only + документированный деплой |
| OAuth «с нуля на Flask» vs существующий Supabase Auth | Рекомендация: providers в Supabase |
| Шаг 5 платежи не в продуктовом ТЗ | Опциональный gate G7 |

### 9.5. Выводы и рекомендации

- Начинать с **GitHub Actions CI** (lint/test), даже если auto-deploy отложим.
- OAuth2 — через Supabase Providers.
- Платежи — пропускать, если нет бизнес-требования.
- Не подключать новые MCP без явного OK пользователя.

---

## 10. Журнал шагов ДЗ

| Шаг ДЗ | Тема | Issue | Статус | Примечание |
|--------|------|-------|--------|------------|
| 0 | План + каркас `cicd_integrations_documentation.md` | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done (awaiting OK)** | G1 A; **G2 C**; **G3 N/A**; G4 local; G5 C; G6 A; G7 skip; G8 A; G9 agent |
| 1 | CI/CD пайплайн | [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) | done (awaiting OK) | `.github/workflows/ci.yml`; **G2=B** FE → GitHub Pages |
| 2 | Аудит безопасности | [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) | done (awaiting OK) | remediations A2/B1a/B2a/B3a/C1/C2; → `docs/SECURITY_AUDIT.md` |
| 3 | OAuth2 | [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) | **done (awaiting live Google Console URI)** | Google Enabled in Supabase; FE `signInWithOAuth`; Redirect URLs×3; Console URI = Supabase callback |
| 4 | Аналитика | [#41](https://github.com/Sintik1/Qa_Asistant/issues/41) | done (awaiting OK) | counter `113444012`; live tag/hit/`auth_login` verified; → `docs/METRIKA_SETUP.md` §5.1 |
| 5 | Платежи | — | **skipped** | G7 |
| 6 | Мониторинг | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done (awaiting OK)** | UptimeRobot docs + health `checks`; → `docs/UPTIME_SETUP.md` §7; отдельная Issue UI недоступна — трек в эпике |
| 7 | Логирование | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done (awaiting OK)** | scenarios + redact + `docs/LOGGING.md` §8; отдельная Issue UI недоступна — трек в эпике |
| 8 | Тесты + оптимизация | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done (awaiting OK)** | → `docs/INTEGRATIONS_QA_STEP8.md`; Google redirect URI config residual |
| 9 | Docs + README | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done (awaiting OK)** | `integration_documentation.md` + `security_audit.md` + README; **G2=B Pages deploy** |
| — | Pages one-time setup | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | **done** | Pages Source=Actions; Variables `VITE_SUPABASE_*`; `source-map-js@1.2.2`; CI [#25](https://github.com/Sintik1/Qa_Asistant/actions/runs/37422990061) green → https://sintik1.github.io/Qa_Asistant/ |

---

_Последнее обновление: 2026-10-06 — first GitHub Pages deploy green (`status.json` 200)._
