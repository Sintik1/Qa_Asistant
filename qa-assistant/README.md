# QA Assistant (frontend)

React + TypeScript + Vite + Tailwind CSS — UI для **QA Assistant**.

---

## Требования

| Способ запуска | Что нужно |
|----------------|-----------|
| Docker | Docker Desktop |
| Локально | Node.js 20+, npm 10+ |

---

## Запуск в Docker (рекомендуется)

Команды выполняйте из **корня репозитория** (рядом с `docker-compose.yml`):

```bash
docker compose up --build
```

- Приложение: **http://localhost:8080**
- Контейнер: `qa-assistant`
- Порт хоста: `8080` → порт контейнера `80` (nginx)

Фоновый режим:

```bash
docker compose up --build -d
```

Логи:

```bash
docker compose logs -f qa-assistant
```

Остановка:

```bash
docker compose down
```

Пересборка без кэша:

```bash
docker compose build --no-cache
docker compose up -d
```

Файлы Docker:

- `../docker-compose.yml`
- `Dockerfile`
- `nginx.conf`
- `.dockerignore`

---

## Запуск без Docker (dev с HMR)

### 1. Проверить Node.js и npm

```bash
node -v   # нужно 20+
npm -v    # нужно 10+
```

Если не установлено: https://nodejs.org/ (LTS).  
После установки откройте новый терминал и повторите команды выше.

### 2. Перейти в папку frontend

Из корня репозитория:

```bash
cd qa-assistant
```

### 3. Скачать зависимости

```bash
npm install
```

Что происходит:
- npm читает `package.json` и `package-lock.json`;
- скачивает зависимости проекта в `node_modules/`;
- ставит React, Vite, Tailwind, TypeScript, react-router-dom и dev-инструменты.

Если установка упала или `node_modules` повреждён:

```bash
rm -rf node_modules
npm install
```

Обновить зависимости по lock-файлу (как в CI):

```bash
npm ci
```

### 4. Запустить dev-сервер

```bash
npm run dev
```

Приложение: **http://localhost:5173**  
Остановка: `Ctrl+C`.

### 5. Production-сборка локально

```bash
npm run build
npm run preview
```

---

## Быстрая проверка UI

1. **Настройки** → сохранить любой API-токен.
2. Загрузить файл требований (`.pdf`, `.docx`, `.doc`, `.md`).
3. **Генерировать тест-кейсы**.
4. **Скачать CSV** / **Скачать DOCX**.

Маркеры в имени файла для негативных сценариев: `empty`, `fail`, `corrupt`, `slow`.

---

## Маршруты

| Path | Страница | Источник |
|------|----------|----------|
| `/` | HomePage | Figma + ТЗ |
| `/settings` | SettingsPage | ТЗ §3.5 |

---

## Структура `src/`

```
src/
  components/
    layout/        # Header, AppNav, AppLayout
    upload/        # загрузка файлов
    form/          # задача, промт, проект
    management/    # промты / шаблоны
    generation/    # результаты, чанкинг
    ui/            # Button, ProgressBar, ErrorMessage
  hooks/
  mocks/
  pages/
  types/
  utils/
  App.tsx
  main.tsx
  index.css
```
