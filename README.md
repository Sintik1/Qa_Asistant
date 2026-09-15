# QA Assistant

Веб-приложение для генерации тест-кейсов из документов требований (PDF / DOCX / DOC / Markdown).

Сейчас доступен **frontend** (React + TypeScript + Vite + Tailwind) с mock-генерацией без бэкенда.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

---

## Быстрый запуск (Docker)

Нужен установленный и запущенный **Docker Desktop**.

Из корня репозитория:

```bash
docker compose up --build
```

Открыть в браузере: **http://localhost:8080**

Остановить:

```bash
docker compose down
```

Пересобрать образ без кэша:

```bash
docker compose build --no-cache
docker compose up -d
```

Проверить, что контейнер работает:

```bash
docker compose ps
```

---

## Запуск без Docker (локальная разработка)

Нужны **Node.js 20+** и **npm 10+** (npm идёт вместе с Node.js).

### 1. Проверить, что Node и npm установлены

```bash
node -v
npm -v
```

Ожидается, например: `v20.x` / `v22.x` и npm `10+`.  
Если команд нет — установите Node.js LTS: https://nodejs.org/

### 2. Скачать (клонировать) репозиторий

```bash
git clone https://github.com/Sintik1/Qa_Asistant.git
cd Qa_Asistant
```

Если репозиторий уже скачан — просто перейдите в его корень.

### 3. Установить зависимости frontend

```bash
cd qa-assistant
npm install
```

Команда читает `package.json` / `package-lock.json` и скачивает пакеты в папку `node_modules/`  
(React, Vite, Tailwind, TypeScript и т.д.). Первый запуск может занять 1–3 минуты.

Повторная установка (если что-то сломалось):

```bash
rm -rf node_modules
npm install
```

### 4. Запустить приложение в режиме разработки

```bash
npm run dev
```

Открыть в браузере: **http://localhost:5173**  
Остановка сервера: `Ctrl+C` в терминале.

### 5. (Опционально) Production-сборка локально

```bash
cd qa-assistant
npm run build
npm run preview
```

---

## Что проверить после запуска

1. Откройте **Настройки** → сохраните любой API-токен (mock в `localStorage`).
2. На главной загрузите файл `.pdf` / `.docx` / `.doc` / `.md`.
3. Нажмите **Генерировать тест-кейсы**.
4. Скачайте **CSV** или **DOCX**.

Негативные сценарии (по имени файла): `empty`, `fail`, `corrupt`, `slow`.

---

## Тестирование и отчёты

| Документ / команда | Назначение |
|--------------------|------------|
| [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md) | Отчёт о тестировании и проверке **адаптивной вёрстки** (матрица устройств, баги R1/R2, полный регресс) |
| [`development_report.md`](development_report.md) | Журнал стадий разработки + Issues |
| [`tests/README.md`](tests/README.md) | Автотесты: Vitest (unit) и Selenium (UI/security) |

Unit-тесты frontend:

```bash
cd qa-assistant
npm test
npm run build
```

UI E2E (нужен запущенный app):

```bash
cd tests
QA_ASSISTANT_BASE_URL=http://localhost:5173 pytest -m "ui or security" -v
```

Issues по тестированию адаптивa и регрессу: [#14](https://github.com/Sintik1/Qa_Asistant/issues/14), [#15](https://github.com/Sintik1/Qa_Asistant/issues/15).

---

## Структура проекта

| Путь | Назначение |
|------|------------|
| `qa-assistant/` | Frontend (React + Vite) |
| `docker-compose.yml` | Запуск UI в Docker на порту 8080 |
| `docs/TESTING_REPORT.md` | Отчёт о тестировании / адаптив |
| `tests/` | Автотесты (Vitest utils в `qa-assistant`, Selenium в `tests/`) |
| `technical_specification.md` | Техническое задание |
| `user_stories.md` | User stories |
| `development_report.md` | Отчёт по стадиям разработки |

Подробнее по frontend: [`qa-assistant/README.md`](qa-assistant/README.md)

---

## Полезные ссылки

- Issue Docker: https://github.com/Sintik1/Qa_Asistant/issues/7
- Issue адаптив-тест: https://github.com/Sintik1/Qa_Asistant/issues/14
- Issue fix R1/R2 + регресс: https://github.com/Sintik1/Qa_Asistant/issues/15
- UI: `/` — написание тест-кейсов, `/settings` — API-токен
