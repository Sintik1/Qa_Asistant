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
9. Баг-хантинг UI через DevTools/CDP — **done** (см. [#9](https://github.com/Sintik1/Qa_Asistant/issues/9)): критичных P0 — **0**; high — 4
10. Автотесты по `prompt_templates.md` §5 — **done** (см. [#10](https://github.com/Sintik1/Qa_Asistant/issues/10), commit `e2f2e28`)
11. AI-отладка: мультимодальные скриншоты + интерпретация консоли — **done** (см. [#11](https://github.com/Sintik1/Qa_Asistant/issues/11))
12. Фикс багов B1–B7 из AI-отладки — **in review** (см. [#12](https://github.com/Sintik1/Qa_Asistant/issues/12))
13. Адаптивный дизайн + media queries — **done** (см. [#13](https://github.com/Sintik1/Qa_Asistant/issues/13))
14. Тест адаптивной вёрстки на эмуляторах — **done** (см. [#14](https://github.com/Sintik1/Qa_Asistant/issues/14)): P0 — **0**; medium — 1; low — 1
15. Fix R1/R2 + полный регресс — **done** (см. [#15](https://github.com/Sintik1/Qa_Asistant/issues/15)): R1/R2 закрыты; регресс green
16. Behavior-preserving refactor — **done** (см. [#16](https://github.com/Sintik1/Qa_Asistant/issues/16), commit `6dc1eed`)

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
| Prompt template (Role/Task/Context/Format) | `prompt_templates.md` §1 → Stage 6; §5 → Stage 10 tests |
| Mock-first без бэкенда | `mockGenerateTestCases` + токен в localStorage |
| Browser CDP bug hunt | `cursor-ide-browser` + `browser_cdp` (fallback: chrome-devtools MCP недоступен) |
| Page Object + Fluent API + parametrize | Selenium E2E в `tests/`; Vitest unit в `qa-assistant/src/utils/*.test.ts` |
| Мультимодальный разбор скриншотов | Stage 11: browser screenshots → visual bug hypotheses |
| AI-интерпретация console/runtime | CDP console hook + Vite log; отличить app errors от debug-probe |
| Prompt template §1 (адаптив) | Stage 13: план → код → типы → пример; проверка ×3; без commit без OK |
| Mobile-first + explicit `@media` | CSS vars + `@media` в `index.css` + Tailwind + `useBreakpoint` |
| Device emulation matrix | chrome-devtools MCP `emulate` + DOM overflow/touch audit script |
| Cross-check visual + metrics | cursor-ide-browser CDP screenshots vs `getBoundingClientRect` |
| Fix → verify loop | Stage 15: правки touch targets → Vitest/build → emulator regression suite |
| Prompt template § refactor (Role/Task) | Stage 16: анализ → proposal → gate «не менять без OK» |

---

## 3. Примеры промптов и результатов

### Промпт: рефакторинг без изменения поведения (`prompt_templates.md` §)

**Запрос:** Role Senior Python Developer + Task «отрефактори код» + ограничения (API/deps/форматы) + Format (список → код → риски) + «без согласия код не менять».

**Результат:** код применён после «ок все»:
- `formStyles.ts`, `triggerBlobDownload.ts`, `GenerationAlerts.tsx`
- cleanup `useTestCaseGeneration` / `mockGeneration` markers
- `CASE_FIELDS` в `GenerationResults`; `BasePage.fill`
- Vitest: **58/58** passed; commit/close Issue — после OK пользователя

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

### Промпт: Stage 13 — адаптивный дизайн

**Запрос:** Senior Frontend Engineer; адаптив под любые устройства + генерация media queries; формат `prompt_templates.md` (19–24); без коммита без согласования.

**Результат:**
- Issue [#13](https://github.com/Sintik1/Qa_Asistant/issues/13)
- Breakpoints: `types/breakpoints.ts`, `utils/breakpoints.ts`, hooks `useMediaQuery` / `useBreakpoint`
- Явные `@media` (sm/md/lg/xl, touch, print, ≤374px) в `index.css`
- Layout/CTA/таблица: `AppLayout`, `Header`, `AppNav`, `GenerationResults` (карточки &lt; md), `Button`, формы

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

### Промпт: Stage 9 — chrome-devtools bug hunt

**Запрос:** протестировать приложение через chrome-devtools-mcp на баги; ответить сколько критичных и где.

**Результат:**
- `user-chrome-devtools` MCP: discovery error / auth timeout → fallback CDP через `cursor-ide-browser`
- Прогон: http://localhost:5173 и http://localhost:8080
- Happy-path OK: upload → token → generate → CSV/DOCX; негативы `empty`/`fail`/`corrupt`/zero-byte OK
- **Критических (P0): 0**
- High: имя CSV ≠ UI; `prompt`/`taskName`/шаблоны не влияют на генерацию; stale `generation.error`; мёртвые кнопки ManagementCard
- Issue [#9](https://github.com/Sintik1/Qa_Asistant/issues/9)

---

### Промпт: Stage 10 — тесты (prompt_templates §5)

**Запрос:** Senior Automation QA; pytest/Selenium; unit+API+UI; Page Object, Fluent API, parametrize; XSS/SQLi; без flaky; формат: сценарии → файлы → моки; вердикт пользователя обязателен.

**Результат:**
- Unit Vitest: 53 теста (бизнес-utils + security sanitization) — `npm test` green
- UI/Security: `tests/` (pytest + Selenium, Page Object + Fluent API)
- Адаптация: RestAssured/JUnit отброшены (не Java); API = mock + ERROR_MESSAGES
- Issue [#10](https://github.com/Sintik1/Qa_Asistant/issues/10); коммит — после вердикта

---

### Промпт: Stage 11 — AI debugging (screenshots + console)

**Запрос:** применить техники отладки с AI — мультимодальный анализ скриншотов багов; AI-интерпретация ошибок консоли.

**Результат:**
- Скриншоты: `uploads/debug/ai-debug/screenshots/` (invalid format, API fail, success, upload)
- Консоль приложения: uncaught errors **не найдены**; UI-ошибки живут в React state
- Артефакт: `SyntaxError: import.meta` — только от debug `Runtime.evaluate`, не от app
- Баги подтверждены визуально+DOM: CSV name mismatch, stale error, dual «Файл не выбран», Settings copy UX, dead ManagementCard, mock ignores prompt
- Issue [#11](https://github.com/Sintik1/Qa_Asistant/issues/11)

---

### Промпт: Stage 12 — fix bugs from AI debug

**Запрос:** `фиксируй` (B1–B7).

**Результат:**
- B3: CSV download → `Тест кейсы_<название>.csv` (`resolveDownloadCsvFileName` + `buildCsvFileName`)
- B4: смена requirements-файла вызывает `generation.clearError()`
- B1/B2: `FileUploadField` — без дубля empty-текста; reset `input.value` после reject
- B5: `MISSING_TOKEN_ON_SETTINGS` на Settings
- B6: ManagementCard buttons disabled + hint
- B7: mock учитывает `taskName` / `prompt`
- Vitest **56/56** green; `npm run build` OK
- Issue [#12](https://github.com/Sintik1/Qa_Asistant/issues/12)

### Промпт: тест адаптивной вёрстки на эмуляторах (шаг 14)

**Запрос:** senior QA — протестировать адаптив на мобильных/эмуляторах, выдать отчёт с багами.

**Результат:**
- Issue [#14](https://github.com/Sintik1/Qa_Asistant/issues/14)
- Матрица: 320 / 375 / 393 / 430 / 667×375 / 768 / 1024×768 / 1280 / 1440
- P0 layout — 0; R1 medium (touch «настройки» 14px); R2 low (input/select ~38px)
- Cards (&lt;md) / table (≥md) подтверждены на реальной mock-генерации

### Промпт: правь R1/R2 + полный регресс (шаг 15)

**Запрос:** исправить найденные баги и провести полное регрессионное тестирование.

**Результат:**
- Issue [#15](https://github.com/Sintik1/Qa_Asistant/issues/15)
- R1/R2: `min-h-11` на Link/ErrorMessage/form controls; touch CSS для `main a`
- Vitest 58/58; build OK
- Регресс: token/generate/cards/table/negatives/overflow 320–1440 — all PASS; новых багов нет
- Отчёт вынесен в `docs/TESTING_REPORT.md`; ссылки добавлены в корневой / `tests/` / `qa-assistant` README

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
| chrome-devtools MCP недоступен (`spawn npx ENOENT`) | В `~/.cursor/mcp.json`: absolute `npx` + `PATH=~/.local/node/bin`; Reload MCP в Cursor |
| UI обещает `Тест кейсы_<название>.csv`, скачивается `test_cases_*.csv` | Зафиксировано в [#9](https://github.com/Sintik1/Qa_Asistant/issues/9); `buildCsvFileName` не подключён |
| После fail ошибка остаётся при выборе нового файла | `generation.clearError()` не вызывается из `useFileUpload` / смены файла |
| Vitest 3 vs Vite 8: конфликт типов `defineConfig` | Отдельный `vitest.config.ts`; `vite.config.ts` без `test` |
| Шаблон §5 тянет Java (RestAssured/JUnit) | Заменены на Vitest + pytest/Selenium под реальный стек |
| Заявление «100% покрытие всего приложения» | Покрыта бизнес-логика utils (unit) + ключевые UI-сценарии (E2E); не каждый JSX-line |
| `DOM.setFileInputFiles` запрещён в browser CDP | Upload через `DataTransfer` + `change` event в `Runtime.evaluate` |
| chrome-devtools MCP `list_pages` пустой | Fallback: cursor-ide-browser + CDP hooks |
| Console «тишина» при видимых UI-ошибках | Ошибки ТЗ идут в `role=alert`, не в `console.error` — для AI-отладки нужен DOM+скрин, не только console |
| CSV hint vs download name (B3) | `downloadCsv` переведён на `buildCsvFileName` |
| Stale generation.error (B4) | `handleRequirementsChange` → `clearError()` |
| Dual «Файл не выбран» + stale native name (B1/B2) | preview только при selectedFile; `input.value=''` при reject |
| Таблица тест-кейсов ломает узкие экраны | &lt; md — карточки; md+ — таблица в `.app-table-scroll` |
| Нужны именно media queries, не только Tailwind | CSS custom properties + `@media` в `index.css`, синхрон с `BREAKPOINTS` |
| chrome-devtools `take_screenshot` timeout | Опора на `evaluate_script` метрики + cursor-ide-browser screenshots |
| Inline link «настройки» 14px по высоте | Зафиксировано R1 в [#14](https://github.com/Sintik1/Qa_Asistant/issues/14); увеличен hit-area (`min-h-11` + inline-flex) в [#15](https://github.com/Sintik1/Qa_Asistant/issues/15) |
| `body { overflow-x: hidden }` маскирует scrollWidth | Аудит по `getBoundingClientRect` right &gt; vw (элементы не вылезали) |
| Form controls 37–42px на mobile | R2: `min-h-11` на input/select (TaskName, ProjectSelect, Settings, Chunk) |
| Дубли Tailwind input class / blob download / fill+send_keys | Stage 16: shared helpers без смены публичного API |
| Риск «сломать e2e» при рефакторе UI | DOM ids, тексты кнопок, ERROR_MESSAGES, mock markers сохранены |

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
11. Stage 9: P0-блокеров нет; чинить в первую очередь расхождение имени CSV с UI и очистку ошибки при смене файла.
12. Stage 10: unit-тесты гонять в CI сразу; Selenium — после поднятого `npm run dev` / Docker; вердикт пользователя — gate перед коммитом.
13. Stage 11: для UI-багов комбинировать скрин (мультимодалка) + a11y snapshot + CDP; console alone недостаточен, если ошибки только в state.
14. Stage 12: после AI-отладки сразу чинить high (CSV name, stale error), затем UX medium — меньше регрессий к демо.
15. Stage 13: держать breakpoints в одном источнике (`utils/breakpoints.ts` ↔ `index.css`); на phone предпочитать карточки широким таблицам.
16. Stage 14: адаптив готов к демо; перед polish — увеличить touch target у inline «настройки» и при желании у form controls.
17. Stage 15: после UI-фиксов всегда гонять короткий emulator-регресс (R1/R2 + generate + overflow) до commit.
18. Stage 16: рефактор по частям (styles → blob → hook → UI → PO); после — Vitest; commit только по явному OK.

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
| Шаг 9 — Chrome DevTools / CDP bug hunt | [#9](https://github.com/Sintik1/Qa_Asistant/issues/9) | open (результат зафиксирован; закрытие после OK) |
| Шаг 10 — Автотесты (prompt_templates §5) | [#10](https://github.com/Sintik1/Qa_Asistant/issues/10) | completed locally (`e2f2e28`; push/close после OK) |
| Шаг 11 — AI screenshot + console debug | [#11](https://github.com/Sintik1/Qa_Asistant/issues/11) | open (результат в комментарии; закрытие после OK) |
| Шаг 12 — Fix B1–B7 | [#12](https://github.com/Sintik1/Qa_Asistant/issues/12) | open (ожидает вердикт/коммит) |
| Шаг 13 — Адаптив + media queries | [#13](https://github.com/Sintik1/Qa_Asistant/issues/13) | completed (closed), commit `8e46176` |
| Шаг 14 — Тест адаптивной вёрстки (эмуляторы) | [#14](https://github.com/Sintik1/Qa_Asistant/issues/14) | open (отчёт готов; R1/R2 → #15) |
| Шаг 15 — Fix R1/R2 + полный регресс | [#15](https://github.com/Sintik1/Qa_Asistant/issues/15) | completed (отчёт в `docs/TESTING_REPORT.md`; commit в этом цикле) |
| Шаг 16 — Behavior-preserving refactor | [#16](https://github.com/Sintik1/Qa_Asistant/issues/16) | completed, commit `6dc1eed` |

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
