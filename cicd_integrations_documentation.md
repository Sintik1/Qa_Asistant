# CI/CD & Integrations Documentation — QA Assistant

Документ — **артефакт сдачи** домашнего задания «Настройка CI/CD и интеграция сервисов» и живой журнал работ по шагам 1–9.

Репозиторий: https://github.com/Sintik1/Qa_Asistant  
Эпик: [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
Связанные артефакты: [`backend_documentation.md`](backend_documentation.md) · [`development_report.md`](development_report.md) · [`docs/FULL_QA_REPORT.md`](docs/FULL_QA_REPORT.md)

**Стек приложения (база):** React (Vite) + Flask + Supabase Auth/Postgres/Storage + Ollama/Leopold.

### Итог сдачи (шаги 1–9)

| Шаг | Результат | Статус |
|-----|-----------|--------|
| 0 | Каркас документа + план + уточнения | **done (awaiting OK)** — все G1–G9 locked |
| 1 | CI/CD пайплайн | **done (awaiting OK)** — [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) |
| 2 | Аудит безопасности | pending |
| 3 | OAuth2 (Google + Yandex) | pending |
| 4 | Аналитика (Яндекс.Метрика) | pending |
| 5 | Платежи (опционально) | **skipped** (G7) |
| 6 | Мониторинг (UptimeRobot) | pending |
| 7 | Логирование | pending |
| 8 | Тестирование и оптимизация | pending |
| 9 | Оформление + README | pending |

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
| G2 | Что деплоить автоматически | CI-only (см. §0.1) | ✅ **C** — lint/test/build; auto-deploy отключён (локальный AI) |
| G3 | Хостинг frontend | N/A при G2=C | ✅ **N/A** |
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
| `deploy` | deploy | **disabled** (`if: false`) — см. §2.4 |

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

**Отключён** (G2=C). Job `deploy` в workflow существует для соответствия этапу «deploy» в задании, но не запускается.

Чтобы включить позже (Vercel/Railway + Leopold в облаке):
1. Убрать/изменить `if: false` на `if: github.ref == 'refs/heads/main'`.
2. Добавить secrets (`VERCEL_TOKEN`, `RAILWAY_TOKEN`, …).
3. Обновить §0 и README.

**Проверка пайплайна:** после `git push` в GitHub → вкладка **Actions** → workflow **CI**. Локально перед push: команды из §2.3 (на момент реализации: **99** pytest, **78** vitest).

### 2.5. AI-генерация базового пайплайна

Базовый YAML сгенерирован агентом по gate G1/G2 и структуре монорепо; доработки: исключение Selenium-тестов, Ruff scope, TS-fix для green `npm run build`.

---

## 3. Безопасность

> Заполняется на **шаге 2**. Отчёт аудита: раздел ниже + при необходимости `docs/SECURITY_AUDIT.md`.

### 3.1. Dependency audit

- Frontend: `npm audit`
- Backend: `pip-audit` / `safety` (по наличию в окружении)

### 3.2. OWASP Top 10 (чеклист)

| Риск | Текущее состояние (предварительно) | План |
|------|-----------------------------------|------|
| Injection (SQL) | PostgREST / параметризация; string SQL запрещён rules | проверить + тесты |
| XSS | React escaping; проверить `dangerouslySetInnerHTML` | audit FE |
| CSRF | JWT Bearer (не cookie session) — низкий риск classic CSRF | документировать |
| Broken Auth | Supabase + JWT; bypass disabled on PaaS | OAuth hardening |
| Sensitive data | `.env` gitignored | secrets scan в CI |
| Misconfig | CORS whitelist | проверить prod env |
| Vulnerable deps | TBD audit | update |
| Logging/monitoring | JSON logs + health | шаги 6–7 |

### 3.3. Найденные проблемы и исправления

_Таблица заполнится на шаге 2._

| ID | Severity | Находка | Исправление |
|----|----------|---------|-------------|
| — | — | — | — |

---

## 4. OAuth2

> Заполняется на **шаге 3**.

### 4.1. Провайдер

_TBD после G5. Рекомендация: Google (и/или Yandex) через **Supabase Auth → Providers**, без отдельного Flask OAuth server._

### 4.2. Backend

- Проверка JWT как сейчас; возможно mapping `identities` / profile после первого OAuth login.
- Не хранить Client Secret на frontend.

### 4.3. Frontend

- Кнопки «Войти через …» на `/auth`.
- Redirect URL в консоли провайдера + Supabase Redirect URLs.

### 4.4. Тест-план

- Успешный вход
- Отмена / ошибка провайдера
- Получение email / user id в UI и в Flask `g.user_id`

---

## 5. Аналитика

> Заполняется на **шаге 4**.

### 5.1. Сервис

_TBD после G6._

### 5.2. События (черновик)

| Событие | Когда |
|---------|-------|
| `page_view` | роуты Home / Settings / Chat / Auth |
| `auth_login` / `auth_signup` | успех Auth |
| `auth_oauth_start` | клик OAuth |
| `document_upload` | успешный upload |
| `generate_start` / `generate_success` / `generate_error` | генерация |
| `csv_download` | скачивание CSV |

Env: `VITE_ANALYTICS_*` (без секретов в клиенте, только public counter id).

---

## 6. Платежи (опционально)

> Gate G7. Если **A — пропустить**, раздел остаётся с обоснованием «out of scope продукта / опционально по ТЗ ДЗ».

### 6.1. Сервис

_TBD._

### 6.2. Backend / webhook / FE UI

_TBD при выборе B/C._

---

## 7. Мониторинг и Health Check

> Заполняется на **шагах 6** (и частично 1 при деплое).

### 7.1. Существующий endpoint

`GET /api/health` — публичный; отчёт о `persist`, AI, RAG.

### 7.2. План усиления

- Расширить checks: БД (Supabase ping), AI ping (опционально soft-fail), disk/uploads.
- Внешний uptime (UptimeRobot и т.п.) → URL health.
- Алерты: email/Telegram при downtime.

---

## 8. Логирование

> Частично уже реализовано (Backend ДЗ шаг 7). Шаг 7 этого ДЗ — доработка + промпты AI-анализа + (опц.) централизация.

### 8.1. Текущее

- JSON lines, уровни info/warning/error
- `logs/app.log` (rotating) + stdout
- Env: `LOG_LEVEL`, `LOG_JSON`, …

### 8.2. План доработки

- Единый `request_id` уже есть — проверить покрытие всех routes
- Промпты для AI-анализа логов (типовые ошибки Auth, CORS, AI timeout)
- Опционально: отправка в PaaS log drain / Supabase Logs (документировать)

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
| … | … |

### 9.3. Примеры промптов и результатов

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
| 1 | CI/CD пайплайн | [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) | done (awaiting OK) | `.github/workflows/ci.yml`; deploy `if: false` |
| 2 | Аудит безопасности | TBD | pending | |
| 3 | OAuth2 | TBD | pending | Google + Yandex (G5 C) |
| 4 | Аналитика | TBD | pending | Яндекс.Метрика (G6 A) |
| 5 | Платежи | — | **skipped** | G7 |
| 6 | Мониторинг | TBD | pending | UptimeRobot (G8 A) |
| 7 | Логирование | TBD | pending | |
| 8 | Тесты + оптимизация | TBD | pending | |
| 9 | Docs + README | TBD | pending | |

---

_Последнее обновление: 2026-10-05 — шаг 1 CI [#38](https://github.com/Sintik1/Qa_Asistant/issues/38)._
