# QA Assistant (frontend)

React + TypeScript + Vite + Tailwind CSS frontend for **QA Assistant**.

## Requirements

- Node.js 20+ (recommended) **или** Docker Desktop
- npm 10+ (если без Docker)

## Запуск в Docker (рекомендуется)

Из корня репозитория (`ДЗ/`):

```bash
docker compose up --build
```

Приложение: **http://localhost:8080**

Остановка:

```bash
docker compose down
```

Только пересборка образа:

```bash
docker compose build --no-cache
```

## Setup (без Docker)

```bash
cd qa-assistant
npm install
```

## Development (HMR)

```bash
npm run dev
```

App: http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Project structure

```
src/
  assets/reference/   # Figma mockup reference export
  components/
    layout/           # Header, AppNav, AppLayout
    upload/           # FileUploadField, UploadSection
    form/             # TaskNameField, PromptField, ProjectSelect
    management/       # ManagementCard (prompts / templates)
    generation/       # ChunkSettingsForm, GenerationResults
    ui/               # Button, PageHeader, ErrorMessage, ProgressBar
  hooks/              # useFileUpload, useTestCaseGeneration
  mocks/              # mock test cases
  pages/              # HomePage, SettingsPage
  types/              # shared TS types
  utils/              # constants, validation, export
  App.tsx
  main.tsx
  index.css
```

### Routes

| Path         | Page          | Source        |
|--------------|---------------|---------------|
| `/`          | HomePage      | Figma mockup  |
| `/settings`  | SettingsPage  | TZ §3.5       |
