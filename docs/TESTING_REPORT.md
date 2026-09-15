# Отчёт о тестировании — QA Assistant

| Поле | Значение |
|------|----------|
| Проект | QA Assistant (frontend, mock) |
| Репозиторий | https://github.com/Sintik1/Qa_Asistant |
| Дата | 2026-09-15 |
| Стенд | http://localhost:5173 (`npm run dev`) |
| Issues | [#14](https://github.com/Sintik1/Qa_Asistant/issues/14), [#15](https://github.com/Sintik1/Qa_Asistant/issues/15), [#17](https://github.com/Sintik1/Qa_Asistant/issues/17) (layout perf + регресс) |
| Вердикт | **PASS** — Stage 17 layout-оптимизация применена; полный регресс зелёный; P0 = 0 |

---

## 1. Область тестирования

| Область | Что проверялось |
|---------|-----------------|
| Функциональность | Settings (токен), генерация, CSV/DOCX-действия, негативы `empty`/`fail`, очистка ошибки при смене файла |
| Адаптив | Overflow, breakpoints, nav, cards↔table, touch targets ≥44px |
| Регресс после фикса R1/R2 | Повтор матрицы устройств + happy/negative path |
| Автотесты | Vitest unit (`qa-assistant`), build |

Вне scope: реальный Leopold/Flask API, физические устройства (использовались эмуляторы).

---

## 2. Инструменты

| Инструмент | Роль |
|------------|------|
| chrome-devtools MCP | `emulate` viewport, `evaluate_script` (overflow / touch / UI asserts) |
| cursor-ide-browser | CDP `Emulation.setDeviceMetricsOverride`, скриншоты |
| Vitest | Unit-тесты utils |
| Vite build | `tsc -b && vite build` |

---

## 3. Отчёт: адаптивная вёрстка (Stage 14 → 15)

### 3.1 Матрица устройств

| Устройство | Viewport | Overflow-X | Nav | Результаты | После фикса R1/R2 |
|------------|----------|------------|-----|------------|-------------------|
| Narrow xs | 320×568 | нет | stack | — | PASS (`pad-x` 0.75rem, title 1.25rem) |
| iPhone SE | 375×667 | нет | stack | cards | PASS |
| Pixel 5 | 393×851 | нет | row* | cards | PASS |
| iPhone 14 Pro Max | 430×932 | нет | — | cards | PASS |
| iPhone landscape | 667×375 | нет | row (sm+) | — | PASS |
| iPad Mini | 768×1024 | нет | row | **table** | PASS |
| iPad landscape | 1024×768 | нет | row | table | PASS |
| Desktop | 1280×800 | нет | row | table, max 64rem | PASS |
| Wide | 1440×900 | нет | row | table, max 64rem | PASS |

\* на ~393px оба пункта меню могут поместиться в одну строку — ожидаемо.

### 3.2 Критерии адаптив-проверки

- [x] Нет горизонтального overflow страницы (`scrollWidth` / элементы с `right > vw`)
- [x] CSS vars + `@media` синхронны с `BREAKPOINTS` (`sm` 640 / `md` 768 / `lg` 1024 / `xl` 1280)
- [x] `< md` → карточки `.app-case-cards`; `≥ md` → таблица в `.app-table-scroll`
- [x] `.app-actions`: column на phone, row с `sm`
- [x] Nav touch ≥44px (coarse pointer)
- [x] Settings без overflow на phone

### 3.3 Баги адаптив-теста и статус

| ID | Severity | Описание | Статус |
|----|----------|----------|--------|
| R1 | Medium | Ссылка «настройки» была 62×14px | **Fixed** — `inline-flex min-h-11` |
| R2 | Low | input/select 37–42px | **Fixed** — `min-h-11` на form controls |
| — | P0 | Критичный layout-break | Не найдено |

Файлы фикса: `HomePage.tsx`, `ErrorMessage.tsx`, `TaskNameField.tsx`, `ProjectSelect.tsx`, `SettingsPage.tsx`, `ChunkSettingsForm.tsx`, `index.css`.

---

## 4. Отчёт: полный регресс (Stage 15)

### 4.1 Автотесты и сборка

| Проверка | Результат |
|----------|-----------|
| `npm test` (Vitest) | **58/58 PASS** |
| `npm run build` | OK |
| Console errors (эмулятор) | 0 |

### 4.2 Функциональные сценарии (эмулятор)

| ID | Сценарий | Результат |
|----|----------|-----------|
| F1 | Missing token → alert ТЗ + «Настроить токен» ≥44px | PASS |
| F2 | Settings: сохранить токен в `localStorage` | PASS |
| F3 | Generate happy path → «Генерация завершена» | PASS |
| F4 | Phone: cards + кнопки CSV/DOCX/перегенерация ≥44px | PASS |
| F5 | Tablet/Desktop: table + `.app-table-scroll` | PASS |
| F6 | Chunk panel после «Перегенерировать» — controls ≥44px | PASS |
| F7 | `empty.md` → ошибка «не обнаружено требований» | PASS |
| F8 | `fail.md` → ошибка сервиса анализа | PASS |
| F9 | Смена файла очищает ошибку (B4) | PASS |
| F10 | Overflow-матрица 320–1440 после фикса | PASS (0) |

### 4.3 Touch targets после фикса

| Элемент | Высота | Статус |
|---------|--------|--------|
| Link «настройки» | 44px | PASS |
| Task name / project select | 44px | PASS |
| Settings token input | 44px | PASS |
| ErrorMessage action | 44px | PASS |
| Chunk number/select | 44px | PASS |
| Result action buttons | 44px | PASS |

---

## 5. Итог

| Severity | Найдено (Stage 14) | Открыто после Stage 15 |
|----------|--------------------|-------------------------|
| P0 / Critical | 0 | 0 |
| Medium | 1 (R1) | 0 |
| Low | 1 (R2) | 0 |

**Заключение:** адаптивная вёрстка и основной UI-поток пригодны к демо. Регресс после фикса R1/R2 — зелёный. Новых дефектов не обнаружено.

---

## 6. Как воспроизвести проверки

```bash
# Unit
cd qa-assistant && npm test && npm run build

# UI (эмуляторы вручную или через DevTools device toolbar)
cd qa-assistant && npm run dev
# Открыть http://localhost:5173
# DevTools → Device toolbar: 320 / 375 / 768 / 1280
```

Автотесты Selenium: см. [`tests/README.md`](../tests/README.md).

Журнал стадий разработки: [`development_report.md`](../development_report.md).

---

## 7. Stage 17 — layout perf + полный регресс

### 7.1 Изменения UI (после OK)

- CSS dual view: `.app-results-table` / `.app-case-cards` + `@media (min-width: 768px)` (без JS `useBreakpoint`)
- `.app-gradient`, `transition-colors`, `app-progress__bar` + `prefers-reduced-motion`
- `content-visibility` на карточках/строках; flatten `CaseCard`

### 7.2 Баг, пойманный регрессом

| ID | Severity | Описание | Статус |
|----|----------|----------|--------|
| P17-1 | High | Tailwind `md:hidden` перебит `.app-case-cards { display: grid }` → table+cards одновременно | **Fixed** — переключение только через CSS media в `index.css` |

### 7.3 Автотесты / сборка

| Проверка | Результат |
|----------|-----------|
| `npm test` (Vitest) | **58/58 PASS** |
| `npm run build` | OK |
| Console errors | 0 |

### 7.4 Эмулятор-матрица (overflow)

| Viewport | Overflow-X | Results view | Статус |
|----------|------------|--------------|--------|
| 320×568 | 0 | cards | PASS (`pad-x` 0.75rem) |
| 375×667 | 0 | cards only (`table` display:none) | PASS |
| 768×1024 | 0 | table only (`cards` display:none) | PASS |
| 1024×768 | 0 | table, max-width 56rem | PASS |
| 1280×800 | 0 | table, max-width 64rem | PASS |
| 1440×900 | 0 | table, max-width 64rem | PASS |

### 7.5 Функциональный регресс

| ID | Сценарий | Результат |
|----|----------|-----------|
| F1 | Missing token → точный текст ТЗ + «Настроить токен» 44px | PASS |
| F2 | Settings: token input 44px, overflow 0 | PASS |
| F3 | Happy path → «Генерация завершена», 3 кейса | PASS |
| F4 | Phone: cards + CSV/DOCX/переген ≥44px | PASS |
| F5 | ≥768: table only | PASS |
| F7 | `empty.md` → «не обнаружено требований» | PASS |
| F8 | `fail.md` → «сервису анализа» | PASS |
| F9 | Смена файла очищает ошибку | PASS |
| F10 | Overflow 320–1440 | PASS (0) |

**Вердикт Stage 17:** PASS.
