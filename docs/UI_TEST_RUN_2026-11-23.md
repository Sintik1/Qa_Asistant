# UI tests — 2026-11-23

Issue: [#46](https://github.com/Sintik1/Qa_Asistant/issues/46)

## Vitest (frontend)

`cd qa-assistant && npm test`

**92 passed** (20 files), ~3.4s. Включает компоненты, страницы (`Auth`, `Chat`, `AuthCallback`) и unit-тесты utils/api.

## Selenium (`pytest -m "ui or security"`)

Требует Chrome + Vite `:5173` + Flask `:5001`. Page Objects: Auth (`/auth`), Settings без поля токена, вкладка «Чат по проекту».

Прогон **вне sandbox** (Chrome стартует): **11 passed**, **1 failed**, **1 error**, ~3.5 мин.

| Тест | Результат |
|------|-----------|
| `test_unauthenticated_root_shows_auth` | PASSED |
| `test_settings_page_shows_token_flag_controls` | PASSED |
| `test_home_generate_success` | FAILED — нет «Скачать CSV» за 120s |
| `test_generate_without_file_keeps_button_disabled` | PASSED |
| `test_invalid_format_rejected` | ERROR — `InvalidSessionId` после падения Chrome |
| `test_empty_file_shows_empty_error` | PASSED |
| `test_nav_chat_page` | PASSED |
| XSS (home ×2, settings ×2) | PASSED |
| SQLi ×2 | PASSED |

Причина generate: live `POST /generate` не вернул CSV (JWT/AI), не локатор кнопки. После timeout Chrome-сессия умерла → следующий тест ERROR.

Повтор **в sandbox Cursor**: Chrome `SessionNotCreated` / Selenium Manager без сети к `chrome-for-testing`.

## Как повторить

```bash
export QA_ASSISTANT_BASE_URL=http://127.0.0.1:5173
.venv/bin/python -m pytest tests/test_ui_e2e.py tests/test_security.py -m "ui or security" -v
```
