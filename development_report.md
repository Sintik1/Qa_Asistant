# Development Report — QA Assistant

Отчёт ведётся по требованию `.cursorrules` (п. 10–11): каждая стадия фиксируется в GitHub Issues и в этом файле.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

---

## 1. Описание процесса разработки

Проект развивается по явному пошаговому плану с согласованием после каждого шага:

1. Инициализация фронтенда (Vite + React + TypeScript + Tailwind) — **done**
2. Публикация в GitHub — **done**
3. Структура UI по Figma + ТЗ — **done** (согласовано: Settings + каркас промтов/шаблонов)
4. Установка Cursor Skills — **done** (Figma + UI/React + backend + data + API + testing + process)
5. Усиление ALWAYS-правил трекинга (Issues + `development_report.md`) — **done** (см. [#5](https://github.com/Sintik1/Qa_Asistant/issues/5))
6. Frontend MVP с mock-генерацией (M1–M3 + S1–S3) — **done** (см. [#6](https://github.com/Sintik1/Qa_Asistant/issues/6), commit `8a05e83`)
7. Docker для frontend (`docker compose`) — **done** (см. [#7](https://github.com/Sintik1/Qa_Asistant/issues/7))
8. README с инструкцией запуска — **done** (см. [#8](https://github.com/Sintik1/Qa_Asistant/issues/8))

Правило процесса: не переходить к следующему шагу без согласования пользователя; при неоднозначности — уточнять, не додумывать. На **каждой** стадии обязательно: GitHub Issue + обновление этого отчёта (`.cursorrules` §10–11 + `.cursor/rules/process-tracking.mdc` with `alwaysApply: true`).

---

## 2. Применённые техники работы с AI

| Техника | Как применялась |
|--------|------------------|
| Пошаговый план + gate согласования | Шаги 1→2→3→4; стоп после каждого шага |
| Уточняющие вопросы | Стек (только frontend), папка, npm, TS, GitHub, Figma URL |
| Workspace rules (`.cursorrules`) | UI React/Tailwind; §10–11 вынесены в ALWAYS + `alwaysApply` rule |
| Always-on process rule | `.cursor/rules/process-tracking.mdc` |
| Design-to-code (Figma MCP) | `get_metadata` → `get_design_context` по макету |
| Project Skills | `.cursor/skills/*` + rule `ui-figma-workflow.mdc` |
| Проверка 3 раза | понимание → выполнение → verify (build/URL/git) |
| Ограничение scope | Не добавлять экраны/библиотеки вне ТЗ и макета |
| Prompt template (Role/Task/Context/Format) | `prompt_templates.md` §1 → Stage 6 mock frontend |
| Mock-first без бэкенда | `mockGenerateTestCases` + токен в localStorage |

---

## 3. Примеры промптов и результатов

### Промпт: инициализация проекта по ТЗ (шаги 1–4)

**Запрос (кратко):** инициализировать проект по `technical_specification.md`, GitHub, структура UI из Figma, установить skills; после каждого шага ждать согласование.

**Результат:**
- Шаг 1: `qa-assistant/` (Vite/React/TS/Tailwind), HMR на http://localhost:5173
- Шаг 2: public repo `Sintik1/Qa_Asistant`
- Шаг 3: каркас UI в `qa-assistant/src/**` (запушен)
- Шаг 4: skills Figma + app (UI/React/backend/data/API/testing/process)

### Промпт: уточнения перед шагом 1

**Запрос:** `1A 2B 3 npm 4 TypeScript 5 Qa_Asistant,public,Sintik1` + Figma URL  

**Результат:** frontend-only в `qa-assistant/`; в GitHub — вся папка `ДЗ`.

### Промпт: согласование шага 2

**Запрос:** `ок b` → https://github.com/Sintik1/Qa_Asistant

### Промпт: Figma → структура UI

**Контекст:** `hb0y0ZVRq7sBtI3K2G33Rk`, node `1:4` (raster mockup).  

**Результат:** `HomePage` + компоненты; `SettingsPage` из ТЗ.

### Промпт: обязательные Issues + отчёт

**Запрос:** использовать `.cursorrules` п. 10–11 на каждом шаге.  

**Результат:** Issues #1–#4, файл `development_report.md`.

### Промпт: согласование шага 3 и переход дальше

**Запрос:** `все ок двигаемся дальше`  

**Результат:** UI закоммичен; #3 closed; выполнен шаг 4 (skills).

### Промпт: расширить skills за пределы Figma

**Запрос:** ставить в проект; добавить то, что пригодится для разработки приложения; формат под наш проект.

**Результат:** добавлены `qa-assistant-react`, `qa-assistant-backend`, `qa-assistant-data`, `qa-assistant-api`, `qa-assistant-testing`, `qa-assistant-process` + rule `backend-data-workflow.mdc`.

### Промпт: согласование шага 4

**Запрос:** `ок`  

**Результат:** Issue #4 closed; план инициализации (шаги 1–4) завершён.

### Промпт: усилить правила трекинга

**Запрос:** улучшить `.cursorrules`, чтобы п. 10–11 применялись всегда.

**Результат:** секция ALWAYS в `.cursorrules`; `process-tracking.mdc` (`alwaysApply: true`); обновлён `qa-assistant-process`; Issue [#5](https://github.com/Sintik1/Qa_Asistant/issues/5).

### Промпт: Stage 6 — frontend MVP (prompt_templates §1)

**Запрос:** Senior Frontend Engineer; реализовать `user_stories.md` без бэкенда; React+TS+Tailwind; mock; без сторонних библиотек; не коммитить без согласования; проверить 3 раза.

**Результат:**
- M1: валидация PDF/DOCX/DOC/MD + превью имени/размера
- M2: mock-генерация + прогресс «Извлечение текста.» / «Генерация тест-кейсов...»
- M3: CSV UTF-8 BOM, имя `test_cases_YYYYMMDD_HHMMSS.csv`
- S1: параметры чанкинга + перегенерация
- S2: минимальный OOXML DOCX без библиотек
- S3: Notification API при длительности >30с и скрытой вкладке
- Issue [#6](https://github.com/Sintik1/Qa_Asistant/issues/6); код локально, коммит — после OK пользователя

---

### Промпт: Stage 7 — Docker

**Запрос:** упаковать приложение в Docker-контейнер для локального запуска.

**Результат:**
- `qa-assistant/Dockerfile` (multi-stage: Node build + nginx)
- `qa-assistant/nginx.conf` (SPA fallback)
- корневой `docker-compose.yml` → http://localhost:8080
- Issue [#7](https://github.com/Sintik1/Qa_Asistant/issues/7)

---

### Промпт: Stage 8 — README запуск

**Запрос:** добавить в README.md информацию по запуску приложения.

**Результат:**
- корневой `README.md` (Docker + npm + проверка UI)
- обновлён `qa-assistant/README.md`
- Issue [#8](https://github.com/Sintik1/Qa_Asistant/issues/8)

---

## 4. Проблемы и решения

| Проблема | Решение |
|----------|---------|
| Node.js не установлен; Homebrew на macOS 13 не поставил Node | Бинарник Node v22.19.0 в `~/.local/node` |
| `gh` CLI отсутствовал | Бинарник `gh` 2.76.2; push через HTTPS + token |
| Figma MCP auth / namespace | `mcp_auth` → повторный discovery |
| Макет Figma — flat PNG | Структура из screenshot + ТЗ; reference PNG в repo |
| `.cursorrules` Flask vs задача React | По 1A — только frontend |
| П. 10–11 не велись с шага 1 | Issues + отчёт; далее — на каждом шаге |
| П. 10–11 были короткими и легко пропускались | Вынесены в ALWAYS + Cursor rule `alwaysApply: true` + чеклист |
| DOCX без сторонних библиотек | Минимальный ZIP(store)+OOXML вручную в `docxExport.ts` |
| Нужны негативные сценарии без API | Маркеры в имени файла: `empty`/`fail`/`corrupt`/`slow` |
| Имя compose-проекта из папки `ДЗ` пустое/невалидное | Явный `name: qa-assistant` в `docker-compose.yml` |

---

## 5. Выводы и рекомендации

1. Gate согласования сохранять.
2. Для pixel-perfect лучше компонентные frames в Figma, не один screenshot.
3. Issues + `development_report.md` обновлять сразу при закрытии шага.
4. Перед детальной вёрсткой: Figma MCP auth + skill `figma-design-to-code`.
5. Skills покрывают весь цикл: UI, API, backend, data, тесты, процесс.
6. Следующая работа: pixel-perfect HomePage и/или каркас Flask-backend.
7. Трекинг стадий теперь enforced через ALWAYS-секцию и `alwaysApply` rule — не полагаться только на краткий пункт в середине файла.
8. Stage 6: mock-фронт закрывает happy-path и основные ошибки ТЗ; реальный extract/AI — только после бэкенда.
9. Stage 6 закоммичен после явного «ок фиксируй» пользователя.
10. Для демо без Node: `docker compose up --build` → http://localhost:8080 (нужен запущенный Docker Desktop).

---

## 6. Журнал стадий (Issues)

| Стадия | Issue | Статус |
|--------|-------|--------|
| Шаг 1 — Инициализация фронтенда | [#1](https://github.com/Sintik1/Qa_Asistant/issues/1) | completed (closed) |
| Шаг 2 — GitHub репозиторий | [#2](https://github.com/Sintik1/Qa_Asistant/issues/2) | completed (closed) |
| Шаг 3 — Структура UI (Figma + ТЗ) | [#3](https://github.com/Sintik1/Qa_Asistant/issues/3) | completed (closed) |
| Шаг 4 — Установка Skills | [#4](https://github.com/Sintik1/Qa_Asistant/issues/4) | completed (closed) |
| Шаг 5 — ALWAYS трекинг (Issues + отчёт) | [#5](https://github.com/Sintik1/Qa_Asistant/issues/5) | completed (closed) |
| Шаг 6 — Frontend MVP (mock M1–M3, S1–S3) | [#6](https://github.com/Sintik1/Qa_Asistant/issues/6) | completed (closed), commit `8a05e83` |
| Шаг 7 — Docker frontend | [#7](https://github.com/Sintik1/Qa_Asistant/issues/7) | completed (closed) |
| Шаг 8 — README: запуск приложения | [#8](https://github.com/Sintik1/Qa_Asistant/issues/8) | completed (closed) |

---

## 7. Stage 4 details — установленные skills

### Application (project)

| Skill | Domain |
|-------|--------|
| `qa-assistant-ui` | Карта экранов / папок |
| `qa-assistant-react` | React/TS/Tailwind |
| `qa-assistant-backend` | Flask / pipeline |
| `qa-assistant-data` | Repository / UoW / SQL |
| `qa-assistant-api` | FE↔BE контракт |
| `qa-assistant-testing` | Pytest / quality |
| `qa-assistant-process` | Issues + отчёт (ALWAYS) |

### Figma (project)

`figma-design-to-code`, `figma-use`, `figma-implement-motion`, `figma-use-motion`, `figma-code-connect`, `figma-generate-design`

### Rules

- `.cursor/rules/process-tracking.mdc` — **alwaysApply: true** (§10–11)
- `.cursor/rules/ui-figma-workflow.mdc`
- `.cursor/rules/backend-data-workflow.mdc`

### Personal mirror (машина)

`~/.cursor/skills/`: core Figma skills

### Как проверить

```bash
ls .cursor/skills
ls .cursor/rules
```

GitHub: https://github.com/Sintik1/Qa_Asistant/tree/main/.cursor
