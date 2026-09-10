# QA Assistant (frontend)

React + TypeScript + Vite + Tailwind CSS frontend for **QA Assistant**.

## Requirements

- Node.js 20+ (recommended)
- npm 10+

## Setup

```bash
cd qa-assistant
npm install
cp .env.example .env
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
    ui/               # Button, PageHeader, ErrorMessage, ProgressBar
  hooks/              # useFileUpload
  pages/              # HomePage, SettingsPage
  types/              # shared TS types
  utils/              # constants, validation, formatters
  App.tsx
  main.tsx
  index.css
```

### Routes

| Path         | Page          | Source        |
|--------------|---------------|---------------|
| `/`          | HomePage      | Figma mockup  |
| `/settings`  | SettingsPage  | TZ §3.5       |
