# Development Report — QA Assistant

Отчёт ведётся по требованию `.cursorrules` (п. 10–11): каждая стадия фиксируется в GitHub Issues и в этом файле.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

---

## 1. Описание процесса разработки

Проект развивается по явному пошаговому плану с согласованием после каждого шага:

1. Инициализация фронтенда (Vite + React + TypeScript + Tailwind)
2. Публикация в GitHub
3. Структура UI по Figma + ТЗ
4. Установка Cursor Skills для UI/Figma-вёрстки *(в работе / ожидает согласования)*

Правило процесса: не переходить к следующему шагу без согласования пользователя; при неоднозначности — уточнять, не додумывать.

---

## 2. Применённые техники работы с AI

| Техника | Как применялась |
|--------|------------------|
| Пошаговый план + gate согласования | Шаги 1→2→3→4; стоп после каждого шага |
| Уточняющие вопросы | Стек (только frontend), папка, npm, TS, GitHub, Figma URL |
| Workspace rules (`.cursorrules`) | Стек UI React/Tailwind; с п. 10–11 — Issues + этот отчёт |
| Design-to-code (Figma MCP) | `get_metadata` → `get_design_context` по макету |
| Проверка 3 раза | Перед закрытием шага: понимание → выполнение → verify (build/URL) |
| Ограничение scope | Не добавлять экраны/библиотеки вне ТЗ и макета |

---

## 3. Примеры промптов и результатов

### Промпт: инициализация проекта по ТЗ (шаги 1–4)

**Запрос (кратко):** инициализировать проект по `technical_specification.md`, GitHub, структура UI из Figma, установить skills; после каждого шага ждать согласование.

**Результат:**
- Шаг 1: `qa-assistant/` (Vite/React/TS/Tailwind), HMR на http://localhost:5173
- Шаг 2: public repo `Sintik1/Qa_Asistant`, initial commit
- Шаг 3: каркас страниц/компонентов/utils по Figma + Settings из ТЗ
- Шаг 4: ещё не стартовал (ожидает согласования шага 3 / этого правила)

### Промпт: уточнения перед шагом 1

**Запрос пользователя:** `1A 2B 3 npm 4 TypeScript 5 Qa_Asistant,public,Sintik1` + Figma URL

**Результат:** зафиксированы решения без догадок; проект в подпапке `qa-assistant/`, в GitHub — вся папка `ДЗ` (вариант B).

### Промпт: согласование шага 2

**Запрос:** `ок b`

**Результат:** создан и запушен https://github.com/Sintik1/Qa_Asistant

### Промпт: Figma → структура UI

**Контекст:** файл `hb0y0ZVRq7sBtI3K2G33Rk`, node `0:1` / `1:4`.

**Результат:** в Figma один растровый экран «Написание тест-кейсов»; собрана компонентная структура + `SettingsPage` (MUST HAVE из ТЗ).

---

## 4. Проблемы и решения

| Проблема | Решение |
|----------|---------|
| Node.js не установлен; Homebrew на macOS 13 не смог поставить Node (`Cellar` / долгая сборка) | Официальный бинарник Node v22.19.0 в `~/.local/node` |
| `gh` CLI отсутствовал | Установлен бинарник `gh` 2.76.2; push через HTTPS + `GITHUB_TOKEN` |
| Figma MCP требовал auth / временно пропадал из namespace | `mcp_auth` → повторный discovery tools |
| Макет Figma — flat PNG, не компонентные слои | Структура UI выведена из screenshot + ТЗ; reference сохранён в `src/assets/reference/` |
| Конфликт `.cursorrules` (Flask/Jinja) vs задача (React/Vite) | По ответу пользователя выбран frontend-only (1A); Flask-структура не разворачивалась |
| П. 10–11 `.cursorrules` не применялись на шагах 1–3 | Исправлено: Issues + этот `development_report.md` (обязательно на каждом шаге далее) |

---

## 5. Выводы и рекомендации

1. Gate согласования снижает риск «додумывания» — сохранять.
2. Для pixel-perfect вёрстки лучше иметь в Figma отдельные frames/components, а не один screenshot.
3. Issues + `development_report.md` вести **сразу при закрытии шага**, не постфактум.
4. Перед шагом 4 согласовать: оставлять ли `SettingsPage` и каркас «Управление промтами/шаблонами».
5. Skills для Figma design-to-code ставить до детальной вёрстки (шаг 4).

---

## 6. Журнал стадий (Issues)

| Стадия | Issue | Статус |
|--------|-------|--------|
| Шаг 1 — Инициализация фронтенда | [#1](https://github.com/Sintik1/Qa_Asistant/issues/1) | completed (closed) |
| Шаг 2 — GitHub репозиторий | [#2](https://github.com/Sintik1/Qa_Asistant/issues/2) | completed (closed) |
| Шаг 3 — Структура UI (Figma + ТЗ) | [#3](https://github.com/Sintik1/Qa_Asistant/issues/3) | awaiting approval (open) |
| Шаг 4 — Установка Skills | [#4](https://github.com/Sintik1/Qa_Asistant/issues/4) | pending (open) |
