# Development Report — QA Assistant

Отчёт ведётся по требованию `.cursorrules` (п. 10–11): каждая стадия фиксируется в GitHub Issues и в этом файле.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

---

## 1. Описание процесса разработки

Проект развивается по явному пошаговому плану с согласованием после каждого шага:

1. Инициализация фронтенда (Vite + React + TypeScript + Tailwind) — **done**
2. Публикация в GitHub — **done**
3. Структура UI по Figma + ТЗ — **done** (согласовано: Settings + каркас промтов/шаблонов)
4. Установка Cursor Skills для UI/Figma-вёрстки — **done, ожидает согласования**

Правило процесса: не переходить к следующему шагу без согласования пользователя; при неоднозначности — уточнять, не додумывать. На каждом шаге: GitHub Issue + обновление этого отчёта.

---

## 2. Применённые техники работы с AI

| Техника | Как применялась |
|--------|------------------|
| Пошаговый план + gate согласования | Шаги 1→2→3→4; стоп после каждого шага |
| Уточняющие вопросы | Стек (только frontend), папка, npm, TS, GitHub, Figma URL |
| Workspace rules (`.cursorrules`) | UI React/Tailwind; п. 10–11 — Issues + этот отчёт |
| Design-to-code (Figma MCP) | `get_metadata` → `get_design_context` по макету |
| Project Skills | `.cursor/skills/*` + rule `ui-figma-workflow.mdc` |
| Проверка 3 раза | понимание → выполнение → verify (build/URL/git) |
| Ограничение scope | Не добавлять экраны/библиотеки вне ТЗ и макета |

---

## 3. Примеры промптов и результатов

### Промпт: инициализация проекта по ТЗ (шаги 1–4)

**Запрос (кратко):** инициализировать проект по `technical_specification.md`, GitHub, структура UI из Figma, установить skills; после каждого шага ждать согласование.

**Результат:**
- Шаг 1: `qa-assistant/` (Vite/React/TS/Tailwind), HMR на http://localhost:5173
- Шаг 2: public repo `Sintik1/Qa_Asistant`
- Шаг 3: каркас UI в `qa-assistant/src/**` (запушен)
- Шаг 4: skills в `.cursor/skills/` + rule (ожидает согласования)

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
| Plugin skills не версионировались в repo | Скопированы в `.cursor/skills/` + personal `~/.cursor/skills/` |

---

## 5. Выводы и рекомендации

1. Gate согласования сохранять.
2. Для pixel-perfect лучше компонентные frames в Figma, не один screenshot.
3. Issues + `development_report.md` обновлять сразу при закрытии шага.
4. Перед детальной вёрсткой: Figma MCP auth + skill `figma-design-to-code`.
5. Следующая работа после шага 4: pixel-perfect HomePage по макету (без новых фич).

---

## 6. Журнал стадий (Issues)

| Стадия | Issue | Статус |
|--------|-------|--------|
| Шаг 1 — Инициализация фронтенда | [#1](https://github.com/Sintik1/Qa_Asistant/issues/1) | completed (closed) |
| Шаг 2 — GitHub репозиторий | [#2](https://github.com/Sintik1/Qa_Asistant/issues/2) | completed (closed) |
| Шаг 3 — Структура UI (Figma + ТЗ) | [#3](https://github.com/Sintik1/Qa_Asistant/issues/3) | completed (closed) |
| Шаг 4 — Установка Skills | [#4](https://github.com/Sintik1/Qa_Asistant/issues/4) | awaiting approval (open) |

---

## 7. Stage 4 details — установленные skills

### Project (в репозитории)

```
.cursor/skills/
  qa-assistant-ui/
  figma-design-to-code/
  figma-use/
  figma-implement-motion/
  figma-use-motion/
  figma-code-connect/
  figma-generate-design/
  README.md
.cursor/rules/
  ui-figma-workflow.mdc
```

### Personal (машина разработчика)

`~/.cursor/skills/`: `figma-design-to-code`, `figma-use`, `figma-implement-motion`, `figma-code-connect`

### Как проверить

1. В Cursor видны project skills в `.cursor/skills/`.
2. Figma MCP: аутентифицирован (уже использовался на шаге 3).
3. Файлы в GitHub: https://github.com/Sintik1/Qa_Asistant/tree/main/.cursor
