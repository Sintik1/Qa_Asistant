"""
Автотесты QA Assistant

## Unit (бизнес-логика фронта)

```bash
cd qa-assistant
npm install
npm test
```

Покрывает: fileValidation, formatFileSize, buildCsvFileName,
buildTimestampedFileName, csvExport, mockGenerateTestCases, security sanitization.

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

Примечание: RestAssured/JUnit не используются — стек проекта не Java;
API-интеграция появится после Flask-backend (пока mock на фронте).
"""
