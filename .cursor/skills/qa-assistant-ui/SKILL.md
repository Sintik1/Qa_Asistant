---
name: qa-assistant-ui
description: >-
  Project conventions for QA Assistant UI (React + TypeScript + Tailwind + Vite).
  Use when implementing, styling, or extending screens/components from Figma or TZ;
  when editing qa-assistant/src/**; or when wiring upload/generate/settings UX.
---

# QA Assistant UI

## Stack

- React 19 + TypeScript + Vite + Tailwind CSS v4
- Routing: `react-router-dom`
- App root: `qa-assistant/`

## Before coding UI from Figma

1. Load and follow `.cursor/skills/figma-design-to-code/SKILL.md`.
2. Call Figma MCP `get_design_context` (with `skillNames: figma-design-to-code`) before writing markup.
3. Adapt reference code to existing components in `src/components/**` — do not paste Figma output verbatim.
4. Download assets via MCP / commit under `src/assets/` (remote MCP asset URLs expire).

## Screen map

| Route | Page | Source |
|-------|------|--------|
| `/` | `HomePage` | Figma mockup «Написание тест-кейсов» |
| `/settings` | `SettingsPage` | TZ §3.5 API token |

## Component folders

- `components/layout` — Header, AppNav, AppLayout
- `components/upload` — file upload section
- `components/form` — task name, prompt, project select
- `components/management` — prompts/templates cards
- `components/ui` — Button, PageHeader, ErrorMessage, ProgressBar

## Rules

- Reuse existing components before creating new ones.
- Keep API/business logic out of presentational components.
- Error copy must match `src/utils/constants.ts` (TZ messages).
- Validate uploads with `validateUploadFile` (formats + 100 MB).
- Do not invent screens/features absent from TZ and Figma.
- After each stage: GitHub Issue + update root `development_report.md`.

## Related skills

- `figma-design-to-code` — design → code
- `figma-use` — write/modify nodes in Figma
- `figma-implement-motion` — motion from Figma → code
- `figma-use-motion` — motion tooling in Figma
- `figma-code-connect` — Code Connect mappings
- `figma-generate-design` — code → Figma (only if asked)
