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
  assets/       # static assets
  components/   # reusable UI components (from Figma)
  hooks/        # React hooks
  pages/        # page-level screens
  types/        # TypeScript types
  utils/        # helpers
  App.tsx
  main.tsx
  index.css
```
