---
name: qa-assistant-react
description: >-
  React/TypeScript/Tailwind implementation practices for QA Assistant UI beyond
  Figma import: composition, state, forms, accessibility, routing. Use when
  building or refactoring components in qa-assistant/src without a new Figma
  pull, or together with qa-assistant-ui.
---

# QA Assistant React / UI Engineering

Use with `qa-assistant-ui` (routes/folders) and `figma-design-to-code` (when a Figma node is the source).

## Stack

- React 19 + TypeScript + Vite + Tailwind v4 (`@tailwindcss/vite`)
- Router: `react-router-dom` (`App.tsx`)

## Patterns

- Pages in `pages/` compose feature components; keep pages thin.
- Shared UI in `components/ui`; domain UI in `upload` / `form` / `management` / `layout`.
- Hooks for reusable stateful logic (`hooks/useFileUpload.ts`).
- Types in `types/`; no `any` in public component props.

## Tailwind

- Utility-first; prefer existing color language (violet / orange / green from mockup).
- Theme tokens via CSS `@theme` in `index.css` when extending.
- Avoid new UI libraries unless explicitly requested.

## UX from TZ

- Show file **name + size** after select.
- Enable primary action only when requirements file is valid.
- Use `ErrorMessage` + `ProgressBar` for TZ flows.
- Copy from `utils/constants.ts` only.

## Accessibility

- Labels tied to inputs (`htmlFor` / `id`).
- `role="alert"` for errors; `aria-live` for progress.
- Buttons: real `<button>` with correct `type`.

## Do not

- Duplicate Figma screenshots as the live UI.
- Put API secrets in Vite `VITE_*` beyond public base URL.
- Add screens not in TZ/Figma without asking.
