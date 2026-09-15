"""
Автотесты QA Assistant

## Отчёты о тестировании

- Полный отчёт (функционал + **адаптивная вёрстка** + регресс): [`docs/TESTING_REPORT.md`](../docs/TESTING_REPORT.md)
- Журнал стадий: [`development_report.md`](../development_report.md)
- Issues: [#14](https://github.com/Sintik1/Qa_Asistant/issues/14), [#15](https://github.com/Sintik1/Qa_Asistant/issues/15)

## Unit (бизнес-логика фронта)

```bash
cd qa-assistant
npm install
npm test
```

Покрывает: fileValidation, formatFileSize, buildCsvFileName,
buildTimestampedFileName, csvExport, mockGenerateTestCases, security sanitization,
breakpoints.

## UI E2E + Security (pytest + Selenium, Page Object + Fluent API)

1. Поднять приложение:
   - `cd qa-assistant && npm run dev` → http://localhost:5173
   - или `docker compose up --build` → http://localhost:8080
2. Установить зависимости:
   ```bash
   python3 -m venv .venv-tests && source .venv-tests/bin/activate
   pip install -r tests/requirements-test.txt
   ```
3. Запуск:
   ```bash
   cd tests
   QA_ASSISTANT_BASE_URL=http://localhost:5173 pytest -m "ui or security" -v
   ```

Маркеры: `ui`, `security`.

## Адаптив (ручная / эмуляторная проверка)

Краткая матрица и критерии — в [`docs/TESTING_REPORT.md`](../docs/TESTING_REPORT.md) §3.
В Chrome DevTools: Device toolbar → 320 / 375 / 768 / 1280; проверить overflow, cards↔table, touch ≥44px.

Примечание: RestAssured/JUnit не используются — стек проекта не Java;
API-интеграция появится после Flask-backend (пока mock на фронте).
"""
