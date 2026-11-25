# Development Report — QA Assistant

Отчёт ведётся по требованию `.cursorrules` (п. 10–11): каждая стадия фиксируется в GitHub Issues и в этом файле.

Репозиторий: https://github.com/Sintik1/Qa_Asistant

---

## 1. Описание процесса разработки

Проект развивается по явному пошаговому плану с согласованием после каждого шага:

1. Инициализация фронтенда (Vite + React + TypeScript + Tailwind) — **done**
2. Публикация в GitHub — **done**
3. Структура UI по Figma + ТЗ — **done** (согласовано: Settings + каркас промтов/шаблонов)
4. Установка Cursor Skills — **done** (Figma + UI/React + backend + data + API + testing + process)
5. Усиление ALWAYS-правил трекинга (Issues + `development_report.md`) — **done** (см. [#5](https://github.com/Sintik1/Qa_Asistant/issues/5))
6. Frontend MVP с mock-генерацией (M1–M3 + S1–S3) — **done** (см. [#6](https://github.com/Sintik1/Qa_Asistant/issues/6), commit `8a05e83`)
7. Docker для frontend (`docker compose`) — **done** (см. [#7](https://github.com/Sintik1/Qa_Asistant/issues/7))
8. README с инструкцией запуска — **done** (см. [#8](https://github.com/Sintik1/Qa_Asistant/issues/8))
9. Баг-хантинг UI через DevTools/CDP — **done** (см. [#9](https://github.com/Sintik1/Qa_Asistant/issues/9)): критичных P0 — **0**; high — 4
10. Автотесты по `prompt_templates.md` §5 — **done** (см. [#10](https://github.com/Sintik1/Qa_Asistant/issues/10), commit `e2f2e28`)
11. AI-отладка: мультимодальные скриншоты + интерпретация консоли — **done** (см. [#11](https://github.com/Sintik1/Qa_Asistant/issues/11))
12. Фикс багов B1–B7 из AI-отладки — **in review** (см. [#12](https://github.com/Sintik1/Qa_Asistant/issues/12))
13. Адаптивный дизайн + media queries — **done** (см. [#13](https://github.com/Sintik1/Qa_Asistant/issues/13))
14. Тест адаптивной вёрстки на эмуляторах — **done** (см. [#14](https://github.com/Sintik1/Qa_Asistant/issues/14)): P0 — **0**; medium — 1; low — 1
15. Fix R1/R2 + полный регресс — **done** (см. [#15](https://github.com/Sintik1/Qa_Asistant/issues/15)): R1/R2 закрыты; регресс green
16. Behavior-preserving refactor — **done** (см. [#16](https://github.com/Sintik1/Qa_Asistant/issues/16), commit `6dc1eed`)
17. Оптимизация вёрстки (perf markup/CSS) — **done** (см. [#17](https://github.com/Sintik1/Qa_Asistant/issues/17)); регресс PASS; commit после OK
18. Selenium fix + Vitest bump + component tests + docs sync — **done** (см. [#18](https://github.com/Sintik1/Qa_Asistant/issues/18), commit `53e1583`)
19. Backend ДЗ — workflow + `backend_documentation.md` + rules (все `.cursorrules` в силе) — **in progress** (см. [#19](https://github.com/Sintik1/Qa_Asistant/issues/19); `backend_documentation.md` §5–§6)
20. Backend ДЗ шаг 1 — проектирование БД (3 варианта схем, gate) — **awaiting choice** (см. [#20](https://github.com/Sintik1/Qa_Asistant/issues/20); детали в `backend_documentation.md` §1.4–1.7)
21. Backend ДЗ шаг 1 — выбор **B** + SQL-миграция — **done (awaiting OK)** (см. [#20](https://github.com/Sintik1/Qa_Asistant/issues/20); `supabase/migrations/20260928143000_init_variant_b.sql`)
22. Backend ДЗ шаг 2 — инфраструктура **A Supabase** (vs self-hosted) — **done (awaiting OK)** (см. [#21](https://github.com/Sintik1/Qa_Asistant/issues/21); `backend_documentation.md` §2.0)
23. Backend ДЗ шаг 3 — MCP + deploy schema на `revyywfeeqdmlgrbakpj` — **done (awaiting OK)** (см. [#22](https://github.com/Sintik1/Qa_Asistant/issues/22); §2.2)
24. Backend ДЗ шаг 4 — API endpoints (варианты A/B/C, gate) — **awaiting choice** (см. Issue шаг 4; `backend_documentation.md` §3)
25. Backend ДЗ шаг 4 — выбран **C** + Flask API + Qwen/Leopold — **done (awaiting OK)** (см. [#23](https://github.com/Sintik1/Qa_Asistant/issues/23); pytest 8/8)
26. Ollama + qwen2.5:7b/14b для учёбы (`AI_PROVIDER=ollama`) — **done** (см. [#23](https://github.com/Sintik1/Qa_Asistant/issues/23); pytest 15/15)
27. MacBook Air M1 8GB / macOS 13: Ollama **v0.6.5** + **qwen2.5:1.5b** — **done** (latest Ollama 0.35 требует macOS 14)
28. Тест API + Ollama — **done** (см. [#24](https://github.com/Sintik1/Qa_Asistant/issues/24)): Pytest 16/16, live 17/17)
29. Backend ДЗ шаг 5 — безопасность (Auth/RLS/CORS/secrets) — **done (awaiting OK)** (см. [#25](https://github.com/Sintik1/Qa_Asistant/issues/25); `backend_documentation.md` §1.8)
30. Backend ДЗ шаг 6 — интеграция Frontend ↔ Backend — **done (awaiting OK)** (см. [#26](https://github.com/Sintik1/Qa_Asistant/issues/26); вариант **B**; `backend_documentation.md` §4.4)
31. Backend ДЗ шаг 7 — ошибки и логирование (3 варианта, gate) — **awaiting choice** (см. [#27](https://github.com/Sintik1/Qa_Asistant/issues/27); `backend_documentation.md` §6)
32. Backend ДЗ шаг 7 — выбран **B** + реализация — **done (awaiting OK)** (см. [#27](https://github.com/Sintik1/Qa_Asistant/issues/27); `backend_documentation.md` §3.3.1 / §4.5)
33. Backend extract PDF/DOCX/DOC (3 варианта, gate) — **awaiting choice** (см. [#28](https://github.com/Sintik1/Qa_Asistant/issues/28); `backend_documentation.md` §6)
34. Backend extract — выбран **B** + реализация — **done (awaiting OK)** (см. [#28](https://github.com/Sintik1/Qa_Asistant/issues/28); `backend_documentation.md` §4.6)
35. Backend ДЗ шаг 8 — Full QA (API + UI happy path) — **done (awaiting OK)** (см. [#29](https://github.com/Sintik1/Qa_Asistant/issues/29); live API **23/23**, UI happy path PASS, pytest **59**; `backend_documentation.md` §6)
36. FE Auth page enable — **done** (см. [#29](https://github.com/Sintik1/Qa_Asistant/issues/29)): `VITE_SUPABASE_*` в `.env.local` → `/auth` + RequireAuth)
37. Auth вне общих вкладок — **done (awaiting OK)** (см. [#30](https://github.com/Sintik1/Qa_Asistant/issues/30)): `AuthLayout` без `AppNav`; после login → `AppLayout`
38. DB persistence Supabase (signup + happy path) — **done (awaiting OK)** (см. [#31](https://github.com/Sintik1/Qa_Asistant/issues/31): PostgREST repos; live PASS; pytest 47)
39. Autonomous DB+UI E2E (agent) — **done** (см. [#31](https://github.com/Sintik1/Qa_Asistant/issues/31)): SQL user seed (429 signup), API+Chrome UI PASS, docs updated)
40. Единый отчёт Full QA — **done (awaiting OK)** (см. [#32](https://github.com/Sintik1/Qa_Asistant/issues/32); `docs/FULL_QA_REPORT.md`)
41. Backend ДЗ шаг 9 — оформление сдачи (`backend_documentation.md` + README) — **done** (см. [#33](https://github.com/Sintik1/Qa_Asistant/issues/33), closed; Backend ДЗ шаг 9 → `backend_documentation.md` §5.10 / §6)
42. README для проверяющего (локальный стенд без публичного деплоя) — **done** (см. [#34](https://github.com/Sintik1/Qa_Asistant/issues/34), closed)
43. Рекомендации проверяющего (демо-вход, Table Editor, bypass, compose, screencast) — **done** (см. [#35](https://github.com/Sintik1/Qa_Asistant/issues/35), closed; `ddd6fcf`)
44. RAG на Supabase (pgvector) + section-parser + chat — **done (awaiting OK)** (см. [#36](https://github.com/Sintik1/Qa_Asistant/issues/36); Backend → `backend_documentation.md` §1/§3/§6)
45. RAG независимая проверка + автотесты (user scenarios) — **done (awaiting OK)** (см. [#36](https://github.com/Sintik1/Qa_Asistant/issues/36); pytest **31**, vitest **3**, live smoke memory+Supabase **PASS**)
46. CI/CD + integrations ДЗ — workflow + `cicd_integrations_documentation.md` — **done (awaiting OK)** шаг 0 (см. [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); G1 A, **G2 C**, **G3 N/A**, G4 local, G5 C, G6 A, G7 skip, G8 A)
47. CI/CD ДЗ шаг 1 — GitHub Actions CI — **done (awaiting OK)** (см. [#38](https://github.com/Sintik1/Qa_Asistant/issues/38); CI/CD ДЗ шаг 1 → `cicd_integrations_documentation.md` §2)
48. CI/CD ДЗ шаг 2 — Security audit — **done (awaiting OK)** remediations applied (см. [#39](https://github.com/Sintik1/Qa_Asistant/issues/39); → `docs/SECURITY_AUDIT.md` + §3)
49. CI/CD ДЗ шаг 3 — OAuth2 Google+Yandex — **done (awaiting OK)** (см. [#40](https://github.com/Sintik1/Qa_Asistant/issues/40); → `docs/OAUTH_SETUP.md` + `cicd_integrations_documentation.md` §4)
50. CI/CD ДЗ шаг 4 — Яндекс.Метрика — **done (awaiting OK)** (см. [#41](https://github.com/Sintik1/Qa_Asistant/issues/41); CI/CD ДЗ шаг 4 → `cicd_integrations_documentation.md` §10); counter `113444012`; live verify tag/hit/`auth_login` PASS (`docs/METRIKA_SETUP.md` §5.1)
51. CI/CD ДЗ шаг 6 — мониторинг UptimeRobot + health checks — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); шаг 5 skipped; → `docs/UPTIME_SETUP.md` + `cicd_integrations_documentation.md` §7/§10)
52. CI/CD ДЗ шаг 7 — логирование — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); scenarios + redact; → `docs/LOGGING.md` + `cicd_integrations_documentation.md` §8/§10)
53. CI/CD ДЗ шаг 8 — тестирование интеграций + оптимизация — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); → `docs/INTEGRATIONS_QA_STEP8.md` + `cicd_integrations_documentation.md` §10)
54. CI/CD ДЗ шаг 9 — оформление результатов — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); → `integration_documentation.md` + `security_audit.md` + README; формат сдачи §0)
55. Acceptance fix — G2=B GitHub Pages auto-deploy FE — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); → `docs/DEPLOY_GITHUB_PAGES.md`)
56. Pages one-time setup (agent) — **done** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); Pages+Variables; `source-map-js@1.2.2`; CI deploy green → https://sintik1.github.io/Qa_Asistant/; → `cicd_integrations_documentation.md` §10)
57. OAuth Google via Supabase Auth Providers — **done (awaiting Google Console redirect URI + live smoke)** (см. [#40](https://github.com/Sintik1/Qa_Asistant/issues/40); Dashboard Google Enabled + Redirect URLs; FE `signInWithOAuth`; → `docs/OAUTH_SETUP.md`)
58. Hybrid B — public FE+API, local Ollama — **done (awaiting OK)** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); CI/CD ДЗ → `cicd_integrations_documentation.md` §10; → `docs/HYBRID_LOCAL_AI.md`)
59. Hybrid B restart runbook — **done** (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37); → `docs/HYBRID_B_RESTART.md`; CI/CD ДЗ → `cicd_integrations_documentation.md` §10)
60. Инвентаризация технологий проекта — **done** (см. [#42](https://github.com/Sintik1/Qa_Asistant/issues/42); сводка в чате по манифестам и docs)
61. RAG-чат по проектным данным (вопрос → pgvector → grounded ответ) — **done (awaiting OK)** (см. [#43](https://github.com/Sintik1/Qa_Asistant/issues/43); Backend → `backend_documentation.md` §5.12 / §6)
62. Диагностика «Failed to fetch» на `/auth` — **done (awaiting Clash DIRECT)** (см. [#44](https://github.com/Sintik1/Qa_Asistant/issues/44); Backend → `backend_documentation.md` §6)
63. Auth не падает: причина — **paused Supabase** (NXDOMAIN) + Clash; keepalive + Restore CTA — **done (awaiting Resume в Dashboard)** (см. [#44](https://github.com/Sintik1/Qa_Asistant/issues/44))
64. Полный QA проекта — **done (awaiting OK)** (см. [#45](https://github.com/Sintik1/Qa_Asistant/issues/45); → `docs/FULL_QA_RUN_2026-11-23.md`; pytest 124 / vitest 92 / build pass; live AI/JWT blocked)
65. Все UI-тесты — **done (awaiting OK)** (см. [#46](https://github.com/Sintik1/Qa_Asistant/issues/46); Vitest 92; Selenium 11 pass / 1 fail generate / 1 session error; → `docs/UI_TEST_RUN_2026-11-23.md`)
66. Парсинг DOCX как в TestSites (`TABLE_*`) + нативный Leopold — **done (awaiting OK)** (см. [#47](https://github.com/Sintik1/Qa_Asistant/issues/47); Backend → `backend_documentation.md` §5.13 / §6)
67. Тесты под `TABLE_*`, нативный Leopold и RAG UI — **done (awaiting OK)** (см. [#48](https://github.com/Sintik1/Qa_Asistant/issues/48); pytest 55 на выборке, Vitest Chat+chat API **9**; → `backend_documentation.md` §5.13)
68. RAG по пространству Confluence — **синхронизация выполнена** (см. [#49](https://github.com/Sintik1/Qa_Asistant/issues/49); 3 страницы, 5 чанков у `demo.reviewer`; → `docs/RAG_USAGE.md` §3.5)
69. Переключатель Leopold ↔ локальная Ollama — **включена локальная** (см. [#50](https://github.com/Sintik1/Qa_Asistant/issues/50); `PUT /api/ai/provider`; кнопки в навигации; эмбеддинги остаются hash; → `backend_documentation.md` §5.15)
70. Чат по словам вопроса, а не по шуму hash-вектора — **сделано** (см. [#51](https://github.com/Sintik1/Qa_Asistant/issues/51); «Домофон» выше акции с роутером; → `backend_documentation.md` §5.16)
71. Чат показывает текст страницы дословно — **сделано** (см. [#51](https://github.com/Sintik1/Qa_Asistant/issues/51); модель больше не пересказывает найденный фрагмент)
72. Ответ чата рисуется как Markdown со страницы Confluence — **сделано** (см. [#51](https://github.com/Sintik1/Qa_Asistant/issues/51); нумерованный список «Проект Домофон»)
73. Поиск страниц делает модель эмбеддингов, ответ пишет ИИ — **сделано** (см. [#52](https://github.com/Sintik1/Qa_Asistant/issues/52); `nomic-embed-text`, температура ответа 0; если модель только назвала страницу, в чат идёт её текст)
74. Таблица Confluence в чате и один источник — **сделано** (см. [#53](https://github.com/Sintik1/Qa_Asistant/issues/53); под ответом больше не перечисляются все страницы)
75. Абзацы страницы Confluence в чате не склеиваются — **сделано** (см. [#53](https://github.com/Sintik1/Qa_Asistant/issues/53); страница «Лицей»)
76. Чат показывает все страницы одного уровня сходства — **сделано** (см. [#54](https://github.com/Sintik1/Qa_Asistant/issues/54); вопрос про Домофон и заявку на ТО)
77. Библиотека промптов и шаблонов — **done (awaiting OK)** (см. [#55](https://github.com/Sintik1/Qa_Asistant/issues/55); вариант A; Backend → `backend_documentation.md` §5.20 / §6)
78. Маркер `*Тут текст требований*` — **done (awaiting OK)** (см. [#56](https://github.com/Sintik1/Qa_Asistant/issues/56); длинный файл требований больше не отклоняется лимитом шаблона 20 000; Backend → `backend_documentation.md` §5.21 / §6)
79. Leopold `chatMulti` — **done (awaiting OK)** (см. [#57](https://github.com/Sintik1/Qa_Asistant/issues/57); вариант B: Qwen3 + `user_message`, текст промпта и `max_new_tokens` 15000 сохранены; Backend → `backend_documentation.md` §5.22 / §6)
80. Локальный запуск одной командой `python run.py` — **done (awaiting OK)** (см. [#58](https://github.com/Sintik1/Qa_Asistant/issues/58); Flask :5001 и Vite :5173, общий Ctrl+C; Backend → `backend_documentation.md` §2.4 / §6)

Правило процесса: не переходить к следующему шагу без согласования пользователя; при неоднозначности — уточнять, не додумывать. На **каждой** стадии обязательно: GitHub Issue + обновление этого отчёта (`.cursorrules` §10–11 + `.cursor/rules/process-tracking.mdc` with `alwaysApply: true`). На **шагах backend ДЗ** дополнительно — `backend_documentation.md` (§12); остальные правила разработки (архитектура, тесты, API, секреты, scope ТЗ/Figma) **не ослабляются**.

---

## 2. Применённые техники работы с AI

| Техника | Как применялась |
|--------|------------------|
| Пошаговый план + gate согласования | Шаги 1→2→3→4; стоп после каждого шага |
| Уточняющие вопросы | Стек (только frontend), папка, npm, TS, GitHub, Figma URL |
| Workspace rules (`.cursorrules`) | UI React/Tailwind; §10–11 вынесены в ALWAYS + `alwaysApply` rule |
| Always-on process rule | `.cursor/rules/process-tracking.mdc` |
| Design-to-code (Figma MCP) | `get_metadata` → `get_design_context` по макету |
| Project Skills | `.cursor/skills/*` + rule `ui-figma-workflow.mdc` |
| Проверка 3 раза | понимание → выполнение → verify (build/URL/git) |
| Ограничение scope | Не добавлять экраны/библиотеки вне ТЗ и макета |
| Prompt template (Role/Task/Context/Format) | `prompt_templates.md` §1 → Stage 6; §5 → Stage 10 tests |
| Сверка контракта до кода | Leopold `chatMulti`: пример OpenAPI не копировать; подстановки оставить ([#57](https://github.com/Sintik1/Qa_Asistant/issues/57)) |
| Один процесс-родитель на два сервера | `python run.py` поднимает Flask и Vite и гасит оба по Ctrl+C ([#58](https://github.com/Sintik1/Qa_Asistant/issues/58)) |
| Mock-first без бэкенда | `mockGenerateTestCases` + токен в localStorage |
| Browser CDP bug hunt | `cursor-ide-browser` + `browser_cdp` (fallback: chrome-devtools MCP недоступен) |
| Page Object + Fluent API + parametrize | Selenium E2E в `tests/`; Vitest unit в `qa-assistant/src/utils/*.test.ts` |
| Мультимодальный разбор скриншотов | Stage 11: browser screenshots → visual bug hypotheses |
| AI-интерпретация console/runtime | CDP console hook + Vite log; отличить app errors от debug-probe |
| Prompt template §1 (адаптив) | Stage 13: план → код → типы → пример; проверка ×3; без commit без OK |
| Mobile-first + explicit `@media` | CSS vars + `@media` в `index.css` + Tailwind + `useBreakpoint` |
| Device emulation matrix | chrome-devtools MCP `emulate` + DOM overflow/touch audit script |
| Cross-check visual + metrics | cursor-ide-browser CDP screenshots vs `getBoundingClientRect` |
| Fix → verify loop | Stage 15: правки touch targets → Vitest/build → emulator regression suite |
| Prompt template § refactor (Role/Task) | Stage 16: анализ → proposal → gate «не менять без OK» |
| Prompt template §4 perf layout | Stage 17: узкие места → код → что ускорилось; без OK не менять |
| Quality hardening batch | Stage 18: Selenium order fix, oxlint, Vitest CVE, RTL components, docs |
| DB architect: ТЗ → 3 схемы + gate | Backend ДЗ шаг 1: варианты A/B/C до SQL ([#20](https://github.com/Sintik1/Qa_Asistant/issues/20)) |
| Infra decision matrix (BaaS vs VPS) | Backend ДЗ шаг 2: выбран Supabase ([#21](https://github.com/Sintik1/Qa_Asistant/issues/21)) |
| Supabase MCP auth + apply_migration | Backend ДЗ шаг 3: remote schema на `revyywfeeqdmlgrbakpj` ([#22](https://github.com/Sintik1/Qa_Asistant/issues/22)) |
| API design options + error matrix (gate) | Backend ДЗ шаг 4: A/B/C до реализации |
| Security audit before code (gate) | Backend ДЗ шаг 5: проверка Supabase/RLS/CORS → proposal ([#25](https://github.com/Sintik1/Qa_Asistant/issues/25)) |
| FullStack wire-up proposal + gate | Backend ДЗ шаг 6: FE api/hooks vs mock; варианты A/B/C ([#26](https://github.com/Sintik1/Qa_Asistant/issues/26)) |
| Bypass MCP Issue UI (no Submit) | Issue #26 через `~/.local/bin/gh issue create` |
| Errors/logging options + gate | Backend ДЗ шаг 7: A/B/C → выбран B ([#27](https://github.com/Sintik1/Qa_Asistant/issues/27)) |
| Full QA methodology + gate before execute | Backend ДЗ шаг 8: методика API+UI → OK → live/DevTools → автотесты ([#29](https://github.com/Sintik1/Qa_Asistant/issues/29)) |
| Bypass MCP Issue UI (no Submit) | Issue #29 через `~/.local/bin/gh issue create` |
| Submission doc sync | Шаг 9: итоговый блок в `backend_documentation.md` + README под реальный стек ([#33](https://github.com/Sintik1/Qa_Asistant/issues/33)) |
| Structure-aware parse + RAG design | Leaf-section parser → pgvector index → style/multi-doc/chat ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)) |
| Bypass MCP Issue UI (no Submit) | Issue #36 через `~/.local/bin/gh issue create` |
| CI/CD ДЗ: отдельный артефакт + gate до кода | Шаг 0: `cicd_integrations_documentation.md` + G1–G9 ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Bypass MCP Issue UI (no Submit) | Issue #37 через `~/.local/bin/gh issue create` |
| SPA analytics wrapper + Vitest no-op | CI/CD ДЗ шаг 4: Яндекс.Метрика ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)) |
| MCP Create Issue form invisible → epic comment | CI/CD ДЗ шаг 6 tracked on [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |
| Scenario prompts ×3 + redact before AI | CI/CD ДЗ шаг 7: logging package A ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Integrations QA + apply AI perf fixes | CI/CD ДЗ шаг 8 ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Submission filenames + format checklist | CI/CD ДЗ шаг 9: `integration_documentation.md` + `security_audit.md` ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Manifest-first stack inventory | Чтение `package.json` / `requirements*.txt` / Docker / Actions / миграций, без догадок по README ([#42](https://github.com/Sintik1/Qa_Asistant/issues/42)) |
| RAG retrieve-then-generate | Chat: embedding вопроса → match в БД → LLM только по хитам ([#43](https://github.com/Sintik1/Qa_Asistant/issues/43)) |
| Runtime provider swap | `PUT /api/ai/provider` пересобирает клиент и пишет `AI_PROVIDER`, эмбеддинги не трогает ([#50](https://github.com/Sintik1/Qa_Asistant/issues/50)) |
| Лексический отбор поверх hash | Чат оставляет фрагменты со словами вопроса, заголовок считается ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)) |
| DNS/TLS evidence before blaming Auth form | `scutil --dns` + resolve + curl TLS vs `VITE_SUPABASE_*` ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)) |
| CI-equivalent + live matrix | pytest/vitest/ruff/build, then Flask probes with known env gaps ([#45](https://github.com/Sintik1/Qa_Asistant/issues/45)) |
| Vitest UI + Selenium PO against live Vite | All frontend tests + `pytest -m "ui or security"` on :5173 ([#46](https://github.com/Sintik1/Qa_Asistant/issues/46)) |
| Порт контракта, не второго приложения | DOCX-маркеры и payload Leopold из TestSites внутри текущего upload/generate; Ollama не трогаем ([#47](https://github.com/Sintik1/Qa_Asistant/issues/47)) |
| Тесты на контракт, не на живой токен | Pytest мокает HTTP Leopold и hash-RAG; UI чата — Vitest с моком `chatRequirements` ([#48](https://github.com/Sintik1/Qa_Asistant/issues/48)) |
| Эмбеддинг выбирает страницы, модель пишет ответ | `nomic-embed-text` ранжирует пространство; чат с температурой 0 просит процитировать выбранную страницу. Пустой пересказ заменяется её текстом ([#52](https://github.com/Sintik1/Qa_Asistant/issues/52)) |
| Страница как в Confluence | HTML-таблица → Markdown-таблица, чат рисует `<table>`. Модель выбирает страницу, под ответом остаётся только она ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)) |
| Gate до CRUD библиотеки | Промпты и шаблоны: четыре способа хранения, реализация после выбора. Пустой выбор не меняет generate ([#55](https://github.com/Sintik1/Qa_Asistant/issues/55)) |
| Подстановка маркера промпта | `*Тут текст требований*` заменяется текстом файла. Лимит 20 000 действует на строку библиотеки, не на файл требований ([#56](https://github.com/Sintik1/Qa_Asistant/issues/56)) |

---

## 3. Примеры промптов и результатов

### Промпт: файл требований не встал вместо маркера

**Запрос:** при добавлении файла требований текст не разобрался и не заменил `*Тут текст требований*`. Повторная проверка: не добавился.

**Результат ([#56](https://github.com/Sintik1/Qa_Asistant/issues/56)):** `POST /api/library/extract-text` ответил 422. Текст документа длиннее 20 000 символов, а этот потолок стоял на чтении любого файла. Чтение файла требований этот потолок больше не применяет.

### Промпт: вопрос про Домофон и заявку на ТО отвечает только Домофоном

**Запрос:** ответ некорректный, нужно находить все сходства, без хардкода, система должна работать сама.

**Результат ([#54](https://github.com/Sintik1/Qa_Asistant/issues/54)):** поиск уже ставил «Проект Домофон» (0.771) и «Как делается заявка на ТО» (0.770) рядом. Код оставлял одну страницу. Теперь в ответ входят все страницы, пока следующий балл не ниже предыдущего больше чем на 0.02. Названия страниц в этом правиле не перечислены.

### Промпт: страница «Лицей» снова не как в Confluence

**Запрос:** отображение сломалось, ответ не как на странице.

**Результат ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)):** чат склеивал соседние абзацы в один. Теперь строка страницы остаётся отдельным абзацем, пустой абзац даёт отступ, таблица на месте.

### Промпт: таблица как в Confluence и без лишних требований

**Запрос:** в браузере ответ не таблицей, а под ним перечислены требования со всех страниц.

**Результат ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)):**
- Таблица Confluence сохраняется строками `| Система | ip и порт | какие сервисы |`, сервисы в ячейке через перевод строки
- Чат рисует эту разметку таблицей
- Модель по-прежнему выбирает страницу, но в источники попадает только она, без текста остальных страниц

### Промпт: страницу находит ИИ, а не правила в коде

**Запрос:** не хардкодить выбор страницы; модель сама находит подходящие страницы пространства и отвечает.

**Результат ([#52](https://github.com/Sintik1/Qa_Asistant/issues/52)):**
- Индекс пересобран эмбеддингами `nomic-embed-text` (5 страниц). Слова вопроса в коде страницу больше не выбирают
- «куда активатор ходит при подключении SDP»: ближайшая страница «Проект активатора схема связанностей» (0.721). Ответ — строки таблицы `активатор->SDP 112.000.000:8080`, CRM и ASRZ
- При температуре по умолчанию `qwen2.5:1.5b` выдумывала шаги про Домофон. Чат вызывает модель с температурой 0
- «Как подключить услугу Домофон»: модель назвала страницу и не перенесла список. В ответ подставлен текст этой страницы: «1. Создать заказ» … «6. Проверить подключние в системе»

### Промпт: ответ чата не по странице «Проект Домофон»

**Запрос:** вопрос «Как подключить услугу Домофон» ответился не по странице Confluence, хотя она в индексе.

**Результат ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)):**
- Хеш-эмбеддинги поставили акцию с роутером (сходство 0.064) выше «Проект Домофон» (0.015). Модель `qwen2.5:1.5b` ответила по верхним чужим фрагментам
- Чат теперь оставляет фрагменты, где есть слова вопроса (заголовок тоже). Кейсы без этих слов не попадают в промпт, если требование уже совпало
- Pytest RAG **27 passed**. Переиндексация не нужна
- Следом по тому же запросу: ответ чата — это текст найденного фрагмента, без вызова модели. Вопрос «Как подключить услугу Домофон» возвращает «Инструкция подключения…» как в индексе страницы

### Промпт: переключатель с Leopold на локалку

**Запрос:** сделать переключатель Leopold ↔ локальная модель и сразу включить локальную.

**Результат ([#50](https://github.com/Sintik1/Qa_Asistant/issues/50)):**
- `GET`/`PUT /api/ai/provider`: `ollama` или `leopold`. Процесс пересобирает клиент и пишет `AI_PROVIDER` в `.env`
- В шапке кнопки «Локально» и «Leopold»
- `QA_ASISTANT_MODEL=qwen2.5:1.5b` больше не подставляется в Leopold: у Leopold модель с `/` в имени, иначе `Qwen/Qwen2.5-72B-Instruct`
- Эмбеддинги RAG не менялись (hash), индекс Confluence остаётся совместимым
- Pytest `tests/test_ai_client.py` **11 passed**; Vitest переключателя **1 passed**
- Живой стенд: `AI_PROVIDER=ollama`, Flask перезапущен на `:5001`

### Промпт: попробовать, что нужно для RAG по Confluence

**Запрос:** после обсуждения схемы — сделать первый рабочий контур синхронизации пространства.

**Результат ([#49](https://github.com/Sintik1/Qa_Asistant/issues/49)):**
- `integrations/confluence_client.py`: Cloud basic auth или bearer PAT, HTML → текст, лимит страниц
- `POST /api/rag/confluence/sync` создаёт документ `confluence/{space}/{page}@v{version}` и индексирует его текущим RAG; та же версия пропускается
- Чат: кнопка синхронизации и ссылка «Открыть в Confluence» в цитате
- Pytest `tests/test_confluence_sync.py` и Vitest кнопки — без живого токена
- Чтобы реально обойти пространство, в `.env` нужны `CONFLUENCE_BASE_URL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_SPACE_KEY` (для Cloud ещё `CONFLUENCE_EMAIL`)

### Промпт: перепиши тесты под парсинг/Leopold и покрой RAG, включая UI

**Запрос:** переписать тесты с учётом парсинга `TABLE_*` и Leopold, написать тесты RAG и не забыть UI.

**Результат ([#48](https://github.com/Sintik1/Qa_Asistant/issues/48)):**
- Pytest: секция DOCX держит `TABLE_1_*` внутри листа; upload отдаёт маркеры; generate передаёт их в промпт; `LeopoldNativeClient` читает CSV из поля `response`; RAG индексирует таблицу (`has_table`) и чат возвращает её в цитате
- Vitest `ChatPage`: фильтр документа, выключение кейсов, цитата «Кейс», RAG выключен/неизвестен, пустой индекс, короткая фраза не уходит
- Прогон: pytest выборка **55 passed**; Vitest chat **9 passed**
- Живой Leopold и Selenium против Vite в этом прогоне не запускались

### Промпт: парсинг как в TestSites и интеграция с Leopold

**Запрос:** посмотреть `/Users/vlad/Downloads/TestSites — копия` и настроить парсинг документов и вызов Leopold как в том проекте, не ломая текущий бэкенд.

**Результат ([#47](https://github.com/Sintik1/Qa_Asistant/issues/47)):**
- DOCX-таблицы пишутся маркерами `TABLE_N_START` / `TABLE_N_ROW_*` / `TABLE_BLOCK_*`, заголовки Word остаются `##` для section parser
- `AI_PROVIDER=leopold` ходит в нативный chat API (`uuid` + `chat.system_prompt` + `chat.contents`), ответ читается из поля `response`
- Токен и URL: `LEOPOLD_TOKEN` / `LEOPOLD_API_URL` или прежние `QA_ASISTANT_*`
- Ollama по-прежнему OpenAI-совместимый клиент
- Pytest: `test_doc_reader` + `test_ai_client` + section/upload/generate — **35 passed**

### Промпт: проведи все ui тесты

**Запрос:** прогнать все UI-тесты.

**Результат ([#46](https://github.com/Sintik1/Qa_Asistant/issues/46)):**
- Vitest (все `src/**/*.test.*`) **92 passed** / 20 files
- Selenium вне sandbox: **11 passed**, 1 fail (`test_home_generate_success`, нет CSV за 120s), 1 error (`invalid session` после падения Chrome)
- Повтор в sandbox Cursor: Chrome/Selenium Manager не стартуют
- Отчёт: `docs/UI_TEST_RUN_2026-11-23.md`

### Промпт: проверяй и полностью тестируй весь проект

**Запрос:** полный тест всего проекта.

**Результат ([#45](https://github.com/Sintik1/Qa_Asistant/issues/45)):** `docs/FULL_QA_RUN_2026-11-23.md`
- Hermetic: pytest **124**, vitest **92**, ruff, Vite build
- Live: health/oauth/validation PASS; AI 502 (Ollama down); PostgREST 401 без JWT; Selenium без webdriver_manager
- pip-audit: 4 CVE (dotenv/anyio/pytest)

### Промпт: настрой авторизацию так, чтобы не падала

**Запрос:** настрой всё так, чтобы авторизация не падала.

**Результат ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)):**
- MCP: `Project is paused`; DoH: project host **NXDOMAIN**
- Restore только из Dashboard / Management PAT (агент в Dashboard не залогинен)
- `scripts/supabase_keepalive.py` + `.github/workflows/supabase-keepalive.yml`
- UI `/auth`: CTA Restore при `Failed to fetch`

### Промпт: почему не работает авторизация

**Запрос:** посмотри, почему не работает авторизация.

**Результат ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)):**
- Не логин/пароль и не пустые `VITE_SUPABASE_*`: ключи в `.env.local` на месте
- DNS Mac: Clash TUN `198.18.0.2`; `*.supabase.co` → `240.0.0.162`; TLS `SSL_ERROR_SYSCALL` → UI `Failed to fetch`
- UX: `messageForAuthError` подсказывает DIRECT для `supabase.co`

### Промпт: RAG-чат по проектной информации

**Запрос:** отдельная страница чата с ИИ; вопрос → поиск в БД → наиболее подходящий ответ (RAG).

**Результат ([#43](https://github.com/Sintik1/Qa_Asistant/issues/43)):**
- `RagService.chat` ищет в `document_chunks` и `case_chunks`; цитаты `source_kind`
- UI `/chat`: тред, выбор документа, статус RAG, источники
- Pytest unit (кейсы / skip cases) + Vitest ChatPage/client
- Backend ДЗ → `backend_documentation.md` §5.12 / §6

### Промпт: инвентаризация технологий

**Запрос:** проанализируй проект и напиши, какие технологии использовались для его создания.

**Результат ([#42](https://github.com/Sintik1/Qa_Asistant/issues/42)):**
- Сводка по слоям: React 19 / Vite 8 / TS / Tailwind 4; Flask 3 / Python 3.9–3.11; Supabase (Postgres, Auth, Storage, RLS, pgvector); Ollama/Qwen + Leopold; GitHub Actions + Pages; OAuth; Метрика; UptimeRobot
- Источники: `package.json`, `requirements.txt`, `docker-compose.yml`, `.github/workflows/ci.yml`, `supabase/migrations/`

### Промпт: CI/CD ДЗ шаг 9 — оформление

**Запрос:** docs CI/CD / интеграции / security / мониторинг+логи; README; сверить формат сдачи п.1–4.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- Корневые `integration_documentation.md` (§0 чеклист) и `security_audit.md`
- README блок сдачи; G2=C = инструкции + screencast вместо публичного URL

### Промпт: CI/CD ДЗ шаг 8 — тестирование и оптимизация

**Запрос:** Senior QA; OAuth / Metrika / платежи / CI; AI-оптимизация; исправить баги.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- `docs/INTEGRATIONS_QA_STEP8.md`: матрица PASS/FAIL; платежи N/A
- Fixes: memory persist in bypass tests; `UPLOADS_DIR`; PostgREST 503; FE lazy+manualChunks
- Live: Metrika + Yandex OAuth PASS; Google `redirect_uri_mismatch` (Console)
- Pytest 114 / Vitest 85

### Промпт: CI/CD ДЗ шаг 7 — логирование

**Запрос:** Senior Backend; JSON + централизация (G2=C); промпты×3; после согласования выполнить. Пользователь: «ок».

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- `SCENARIO_PROMPTS` general/auth/cors/ai/persist + `redact_secrets`
- JSON `service`/`env`/`event`; CLI `--scenario`; fixtures; `docs/LOGGING.md`
- Pytest logging suite green; локальная централизация = `logs/app.log`

### Промпт: CI/CD ДЗ шаг 6 — мониторинг

**Запрос:** подтверждаю / переходим дальше; Submit-формы Create Issue нет в UI.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- `core/health.py` checks; `docs/UPTIME_SETUP.md`; `scripts/watch_health.py`
- Pytest health contract; G2=C → UptimeRobot по инструкции + local watcher

### Промпт: CI/CD ДЗ шаг 4 — Яндекс.Метрика

**Запрос:** делать по ДЗ, использовать Яндекс.Метрику.

**Результат ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)):**
- `qa-assistant/src/analytics/metrika.ts` + `MetrikaRouteTracker` (SPA `hit`)
- Goals: auth / upload / generate / csv / chat; env `VITE_YANDEX_METRIKA_ID`
- Docs: `docs/METRIKA_SETUP.md` + `cicd_integrations_documentation.md` §5
- Vitest: disabled without id; init + reachGoal when set

### Промпт: CI/CD ДЗ шаг 2 — security audit

**Запрос:** Senior security; npm audit / pip-audit; OWASP; AI review; сначала отчёт → варианты → после OK фиксы.

**Результат ([#39](https://github.com/Sintik1/Qa_Asistant/issues/39)):**
- Отчёт → gate `делай` → remediations A2/B1a/B2a/B3a/C1/C2
- flask-cors 6; security headers; admin token gate; Settings без localStorage secrets; CI audits
- pytest 101 / vitest 78

### Промпт: CI/CD ДЗ шаг 3 — OAuth2

**Запрос:** Senior FullStack; Google+Yandex (G5=C); secrets только в `.env`; тесты success/error/userinfo.

**Результат ([#40](https://github.com/Sintik1/Qa_Asistant/issues/40)):**
- Google: Supabase `signInWithOAuth`; Yandex: Flask code flow + Admin session
- FE: кнопки + `/auth/callback`; BE: `/api/auth/me`, `/api/auth/oauth/*`
- `scripts/save_oauth_secrets.py` + `docs/OAUTH_SETUP.md`
- pytest oauth + vitest AuthPage; full suite 107 / 81

### Промпт: подробная инструкция после выключения Mac

**Запрос:** сделать подробную инструкцию, как поднять всё заново после reboot.

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):** `docs/HYBRID_B_RESTART.md` (схема, 3 терминала, Pages Variable, проверки, troubleshooting, шпаргалка); ссылка из `docs/HYBRID_LOCAL_AI.md`.

### Промпт: Hybrid B — выложить FE/API, AI на компе

**Запрос:** схема B; настройки сделать самому; Submit в Issue UI не отобразился — «подтверждаю».

**Результат (tracked [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- Runtime: Ollama + Flask на Mac; публичный API через Serveo; Pages Variable `VITE_API_BASE_URL`; CORS `https://sintik1.github.io`
- Артефакты: `docs/HYBRID_LOCAL_AI.md`, `scripts/hybrid_b_start.sh`, `Dockerfile.api`, `render.yaml`
- CI: ruff format fix; Pages deploy на `workflow_dispatch`
- CI/CD ДЗ → `cicd_integrations_documentation.md` §1.1a / §10

### Промпт: CI/CD + integrations ДЗ — план и каркас документации

**Запрос:** Senior developer; пошаговое ДЗ CI/CD / security / OAuth / analytics / payments / monitoring / logging; сначала уточнения; отдельный артефакт как `backend_documentation.md`; трекинг в Issues + `development_report.md`; план; MCP только по согласованию; шаги — отдельными промптами.

**Результат ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)):**
- Создан `cicd_integrations_documentation.md` (разделы 0–10, gate G1–G9)
- Rule `.cursor/rules/cicd-integrations-dz.mdc` (`alwaysApply`)
- MCP Issue form без Submit → Issue через `~/.local/bin/gh`
- CI/CD ДЗ шаг 0 → `cicd_integrations_documentation.md` §10

### Промпт: протестируй RAG + покрой автотестами + user scenarios

**Запрос:** самостоятельно проверить, что RAG работает; покрыть тестами/автотестами; проверить пользовательские сценарии.

**Результат ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)):**
- Live: `scripts/live_rag_smoke.py` — memory PASS; Supabase+demo JWT+Ollama PASS (upload→templates→chat citations→generate→index-cases)
- Pytest: unit + API user scenarios (chat, templates enrich, multi-doc, no auto-index, hierarchical leaves) — **31**
- Vitest: `chat.test.ts` + `ChatPage.test.tsx` — **3**
- Backend ДЗ → `backend_documentation.md` §5.11 / §6

### Промпт: RAG все сценарии + парсер ТЗ

**Запрос:** реализовать RAG (style / multi-doc / chat) на Supabase; парсить объёмные ТЗ по Heading и нумерации (лист раздела = кейс, пункты = шаги); на `Trebovania.docx` ничего не исключать.

**Результат:** Issue [#36](https://github.com/Sintik1/Qa_Asistant/issues/36).
- `core/section_parser.py` + DOCX heading→markdown; `tools/debug_section_parse.py`
- Миграция `document_chunks` / `case_chunks` + RPC `match_*` (768-dim)
- Index on upload; generate обогащается few-shot + related docs; `POST /api/chat` + UI `/chat`
- Pytest: `tests/test_section_parser.py`, `tests/test_rag.py` (22 related green)

### Промпт: рекомендации проверяющего

**Запрос:** учесть feedback: compose только UI; демо-вход + Table Editor checklist; AUTH_DEV_BYPASS вне публичных env; опционально Vercel/Railway или скринкаст.

**Результат:** Issue [#35](https://github.com/Sintik1/Qa_Asistant/issues/35).
- README: демо `demo.reviewer@qatest.local` / `DemoReviewer-2026!`, чеклист Table Editor, compose UI-only, optional PaaS + screencast
- `AUTH_DEV_BYPASS` игнорируется на production/PaaS; pytest **13 passed**
- SQL `scripts/ensure_demo_reviewer.sql`; учётка создана в Supabase
- Screencast: `docs/screencast/happy_path.mp4` (+ GIF/frames), скрипт `scripts/record_happy_path_screencast.py`

### Промпт: README для проверяющего

**Запрос:** актуализировать README — как проверяющий увидит работоспособность без бюджета на деплой.

**Результат:** Issue [#34](https://github.com/Sintik1/Qa_Asistant/issues/34).
- Корневой `README.md`: блок «Для проверяющего» (отчёт / docs / локальный стенд / тесты)
- Явно: публичный деплой не обязателен; стенд = Supabase Free + локальные Flask/Vite/Ollama
- `qa-assistant/README.md` → ссылка на корневой README

### Промпт: Backend ДЗ шаг 9 — оформление сдачи

**Запрос:** оформить результаты ДЗ в `backend_documentation.md` (архитектура, деплой, API, примеры) и обновить README.

**Результат:** Issue [#33](https://github.com/Sintik1/Qa_Asistant/issues/33).
- `backend_documentation.md`: блок «Итог сдачи», актуальный §2.4 полный стек, журнал шаг 9
- `README.md`: FE+BE+Supabase, env, API-таблица, ссылки на docs/QA
- Backend ДЗ шаг 9 → `backend_documentation.md` §5.10 / §6

### Промпт: единый отчёт по тестированию

**Запрос:** зафиксировать всё сделанное по тестированию в единый отчёт.

**Результат:** Issue [#32](https://github.com/Sintik1/Qa_Asistant/issues/32). Файл `docs/FULL_QA_REPORT.md` (API 23/23, UI, Auth layout, DB, фиксы, автотесты, reproduce). Частные отчёты оставлены со ссылкой на сводку.

### Промпт: DB persistence signup + happy path

**Запрос:** полноценно проверить фиксацию в БД при регистрации и happy path; интеграция должна быть рабочей.

**Результат:** Issue [#31](https://github.com/Sintik1/Qa_Asistant/issues/31).
- Gap: Flask был только in-memory → таблицы 0 rows
- Fix: `supabase_rest` + `supabase_store`, `PERSIST_BACKEND=auto`, status mapping
- Live: signup→profile/settings; upload/run/generate → documents/runs/test_cases PASS
- `docs/DB_PERSISTENCE_TEST_REPORT.md`; pytest **47**

### Промпт: Auth UI без общих вкладок

**Запрос:** страница входа/регистрации отдельно, не в поле общих вкладок; после успешной авторизации — основная.

**Результат:** Issue [#30](https://github.com/Sintik1/Qa_Asistant/issues/30).
- `AuthLayout` (Header + form, без `AppNav`)
- `/auth` вне `AppLayout`; `RequireAuth` → после login `Home`/`Settings` с вкладками
- Убрана вкладка «Вход» из `AppNav`
- Verify: Chrome → `/` redirect `/auth`, nav отсутствует

### Промпт: Backend ДЗ шаг 8 — Full QA (methodology → execute)

**Запрос:** Senior Fullstack QA; все API; ошибки; AI-отладка; Chrome DevTools happy path; при green — автотесты. Сначала методика → **ок**.

**Результат:** Issue [#29](https://github.com/Sintik1/Qa_Asistant/issues/29).
- Live API: `scripts/live_api_full_qa.py` → **23/23** (`docs/API_LIVE_TEST_REPORT.md`)
- UI: Chrome DevTools → upload/generate/CSV + reject `.exe` (`docs/UI_HAPPY_PATH_REPORT.md`)
- Fixes: Flask **:5001** (AirTunes на 5000), CORS `127.0.0.1`, `AUTH_DEV_BYPASS` default user
- Autotests: `tests/test_business_logic_full.py` + suite → **59 passed**
- Backend ДЗ шаг 8 → `backend_documentation.md` §5.9 / §6

### Промпт: Backend extract PDF/DOCX/DOC (proposal → B)

**Запрос:** почему нет парсинга → предложить варианты → **`b`**.

**Результат:** Issue [#28](https://github.com/Sintik1/Qa_Asistant/issues/28).
- `core/doc_reader.py` + `POST /api/documents/upload`
- Storage: Supabase bucket / local `uploads/documents/`
- FE: `uploadDocument` вместо stub
- Pytest upload/extract **22** в выборке с generate/smoke/error

### Промпт: Backend ДЗ шаг 7 — ошибки и логирование (proposal → B)

**Запрос:** Senior Backend (errors/logging); сеть 500/401/403, валидация, доступ; логи Flask + Supabase Logs; AI-анализ; сначала 3 варианта, после OK — код, commit/push. Затем **`b`**.

**Результат:** Issue [#27](https://github.com/Sintik1/Qa_Asistant/issues/27).
- BE: `infrastructure/logging_setup.py`, усиленные errorhandlers, `core/log_analyzer.py`, `POST /api/admin/analyze-logs`, `tools/analyze_logs.py`
- FE: `resolveApiError`, `X-Request-Id`, redirect 401/403
- Pytest logging/error **32** (выборка); Vitest `errors.test.ts` **4**
- Docs: `backend_documentation.md` §3.3.1 / §4.5

### Промпт: Backend ДЗ шаг 6 — интеграция FE↔BE (proposal → B)

**Запрос:** Senior FullStack; клиент, API-хуки, load/send, убрать mock; сначала решение, после OK — код, затем коммит. Затем **`b`**.

**Результат:** Issue [#26](https://github.com/Sintik1/Qa_Asistant/issues/26).
- FE: `qa-assistant/src/api/*`, `useTestCaseGeneration` / `useSettingsApi`; Home/Settings без mock-потока
- BE: `POST /api/runs/<id>/generate`, `core/case_parser.py`, `GenerationService`
- Pytest: **24 passed**; npm/Vitest в среде агента недоступны
- Коммит — ждём явной просьбы. Детали: `backend_documentation.md` §4.4

### Промпт: Backend ДЗ шаг 5 — безопасность (gate → реализация)

**Запрос:** Senior Backend + security; Auth, RLS/middleware, CORS, secrets; сначала проверить Supabase, предложить решение, код только после OK. Затем «ок».

**Результат:** Issue [#25](https://github.com/Sintik1/Qa_Asistant/issues/25).
- Supabase **подключена**; выбран **A: Supabase Auth**
- Flask: `app/auth.py` JWT verify; CORS whitelist; `X-User-Id` только testing/dev bypass
- FE: `/auth` signup/login, `RequireAuth`, `@supabase/supabase-js`
- Storage RLS gap-fill migration applied
- Pytest auth+API **26 passed**; Vitest **71**; build OK
- MCP Issue form без Submit → Issue через GitHub REST API

### Промпт: Ollama + Qwen 7B/14B для учёбы

**Запрос:** сразу сделать opensource бесплатный путь Ollama + qwen2.5:7b (или 14B).

**Результат:**
- `integrations/ai_client.py` — factory `AI_PROVIDER=ollama|leopold`
- Default учёба: Ollama `qwen2.5:7b`; `AI_OLLAMA_SIZE=14b` → 14B
- `POST /api/ai/ping`, `scripts/setup_ollama.sh`
- Pytest: **15 passed** (Ollama на машине агента не установлен — нужен локальный install)

### Промпт: Backend ДЗ шаг 4 — выбор C + Qwen + реализация

**Запрос:** `с` + «можно ли Qwen?» + «продолжай».

**Результат:** Issue [#23](https://github.com/Sintik1/Qa_Asistant/issues/23).
- **Да, Qwen** — это модель ТЗ через Leopold (`Qwen/Qwen2.5-72B-Instruct`)
- Hybrid C: Flask CRUD + error contract + Leopold client
- Pytest API: **8 passed**
- Где была форма Issue: в чате Cursor (карточка Create issue); обошли через `~/.local/bin/gh`

### Промпт: Backend ДЗ шаг 4 — API (варианты до кода)

**Запрос:** Senior Backend; ≥3 CRUD; Supabase REST или свой API; все ошибки; сначала варианты, реализация после OK.

**Результат:** варианты A/B/C в `backend_documentation.md` §3; затем выбран C.

### Промпт: Backend ДЗ шаг 3 — MCP + развёртывание

**Запрос:** настроить MCP (`project_ref=revyywfeeqdmlgrbakpj`) и подключиться к проекту.

**Результат:** Issue [#22](https://github.com/Sintik1/Qa_Asistant/issues/22).
- `~/.cursor/mcp.json` → server `supabase` → namespace `user-supabase` (auth OK)
- Project URL: `https://revyywfeeqdmlgrbakpj.supabase.co`
- Applied: `init_variant_b` + `harden_auth_triggers`
- Storage: buckets `documents`/`debug`/`exports` + path policies
- `.env.example` с плейсхолдерами

### Промпт: Backend ДЗ шаг 2 — выбор инфраструктуры

**Запрос:** A Supabase vs B self-hosted Postgres на VPS; обосновать; VPS только если B.

**Результат:** Issue [#21](https://github.com/Sintik1/Qa_Asistant/issues/21).
- Решение: **A Supabase (BaaS)**
- Причины: Auth/RLS/Storage/PostgREST под ДЗ; миграция уже на `auth.users`; Flask остаётся для Leopold; ниже ops и риск сроков
- Self-hosted отклонён → VPS **не готовится**; fallback кратко в `backend_documentation.md` §2.5

### Промпт: Backend ДЗ шаг 1 — выбор B + миграции

**Запрос:** `b`

**Результат:** Issue [#20](https://github.com/Sintik1/Qa_Asistant/issues/20).
- Выбран **Variant B Operational** (6 таблиц)
- Миграция: `supabase/migrations/20260928143000_init_variant_b.sql` (enums, FK, indexes, RLS, signup trigger)
- Корректировки: denormalized `user_id` для RLS; токен не в БД; CHECK 100 МБ
- Документация: `backend_documentation.md` §1.7

### Промпт: Backend ДЗ шаг 1 — проектирование БД

**Запрос:** Role архитектор БД; Task — сущности/связи/поля, SQL, миграции; Context — `technical_specification.md` + `project_description.md`; Format — сначала 2–3 варианта схем на выбор.

**Результат:** Issue [#20](https://github.com/Sintik1/Qa_Asistant/issues/20).
- Требования к данным выведены из MUST/SHOULD/NICE ТЗ
- Варианты: **A** Minimal (4 табл.), **B** Operational (6), **C** Extended (9–10)
- Рекомендация: **B**; миграции после явного выбора
- Фиксация: `backend_documentation.md` §1.4–1.7, §5–§6

### Промпт: Stage 18 — качество frontend (Selenium / Vitest / docs)

**Запрос:** поправить `test_generate_without_token_shows_tz_error` (сначала open, затем clear localStorage); убрать warning в `useMediaQuery.ts`; обновить Vitest (2 medium); добавить component React-тесты; синхронизировать `technical_specification.md` и `.cursorrules` с фактическим frontend-стеком.

**Результат:** Issue [#18](https://github.com/Sintik1/Qa_Asistant/issues/18).
- Selenium: `open_home()` → `localStorage.clear()` → upload/generate
- `useMediaQuery` → `useSyncExternalStore` (lint clean)
- Vitest **4.1.11** (+ Testing Library/jsdom); `npm audit` — **0** vulnerabilities
- Component tests: Button, ErrorMessage, ProgressBar, PageHeader, GenerationAlerts — **71/71** Vitest
- Docs: стек React 19 / TypeScript / Vite / Tailwind v4 в ТЗ и `.cursorrules`


### Промпт: рефакторинг без изменения поведения (`prompt_templates.md` §)

**Запрос:** Role Senior Python Developer + Task «отрефактори код» + ограничения (API/deps/форматы) + Format (список → код → риски) + «без согласия код не менять».

**Результат:** код применён после «ок все»:
- `formStyles.ts`, `triggerBlobDownload.ts`, `GenerationAlerts.tsx`
- cleanup `useTestCaseGeneration` / `mockGeneration` markers
- `CASE_FIELDS` в `GenerationResults`; `BasePage.fill`
- Vitest: **58/58** passed; commit/close Issue — после OK пользователя

### Промпт: оптимизация вёрстки (`prompt_templates.md` §4)

**Запрос:** Role Senior Python Developer + Task «рефакторинг и оптимизация для производительности» + Context (формат результата, без сторонних libs, проверка ×3) + Format (узкое место → код → что ускорилось) + «без согласия не менять». Scope: весь UI `qa-assistant/`.

**Результат (applied + regress):** Issue [#17](https://github.com/Sintik1/Qa_Asistant/issues/17).
- Применено: CSS dual view (`.app-results-table` / `.app-case-cards`), `.app-gradient`, `transition-colors`, progress keyframes, `content-visibility`
- Регресс поймал P17-1 (Tailwind `md:hidden` vs `.app-case-cards { display:grid }`) → фикс через `@media` в `index.css`
- Vitest **58/58**, build OK; эмулятор F1–F10 PASS; отчёт в `docs/TESTING_REPORT.md` §7

### Промпт: инициализация проекта по ТЗ (шаги 1–4)

**Запрос (кратко):** инициализировать проект по `technical_specification.md`, GitHub, структура UI из Figma, установить skills; после каждого шага ждать согласование.

**Результат:**
- Шаг 1: `qa-assistant/` (Vite/React/TS/Tailwind), HMR на http://localhost:5173
- Шаг 2: public repo `Sintik1/Qa_Asistant`
- Шаг 3: каркас UI в `qa-assistant/src/**` (запушен)
- Шаг 4: skills Figma + app (UI/React/backend/data/API/testing/process)

### Промпт: уточнения перед шагом 1

**Запрос:** `1A 2B 3 npm 4 TypeScript 5 Qa_Asistant,public,Sintik1` + Figma URL  

**Результат:** frontend-only в `qa-assistant/`; в GitHub — вся папка `ДЗ`.

### Промпт: согласование шага 2

**Запрос:** `ок b` → https://github.com/Sintik1/Qa_Asistant

### Промпт: Figma → структура UI

**Контекст:** `hb0y0ZVRq7sBtI3K2G33Rk`, node `1:4` (raster mockup).  

**Результат:** `HomePage` + компоненты; `SettingsPage` из ТЗ.

### Промпт: Stage 13 — адаптивный дизайн

**Запрос:** Senior Frontend Engineer; адаптив под любые устройства + генерация media queries; формат `prompt_templates.md` (19–24); без коммита без согласования.

**Результат:**
- Issue [#13](https://github.com/Sintik1/Qa_Asistant/issues/13)
- Breakpoints: `types/breakpoints.ts`, `utils/breakpoints.ts`, hooks `useMediaQuery` / `useBreakpoint`
- Явные `@media` (sm/md/lg/xl, touch, print, ≤374px) в `index.css`
- Layout/CTA/таблица: `AppLayout`, `Header`, `AppNav`, `GenerationResults` (карточки &lt; md), `Button`, формы

### Промпт: обязательные Issues + отчёт

**Запрос:** использовать `.cursorrules` п. 10–11 на каждом шаге.  

**Результат:** Issues #1–#4, файл `development_report.md`.

### Промпт: согласование шага 3 и переход дальше

**Запрос:** `все ок двигаемся дальше`  

**Результат:** UI закоммичен; #3 closed; выполнен шаг 4 (skills).

### Промпт: расширить skills за пределы Figma

**Запрос:** ставить в проект; добавить то, что пригодится для разработки приложения; формат под наш проект.

**Результат:** добавлены `qa-assistant-react`, `qa-assistant-backend`, `qa-assistant-data`, `qa-assistant-api`, `qa-assistant-testing`, `qa-assistant-process` + rule `backend-data-workflow.mdc`.

### Промпт: согласование шага 4

**Запрос:** `ок`  

**Результат:** Issue #4 closed; план инициализации (шаги 1–4) завершён.

### Промпт: усилить правила трекинга

**Запрос:** улучшить `.cursorrules`, чтобы п. 10–11 применялись всегда.

**Результат:** секция ALWAYS в `.cursorrules`; `process-tracking.mdc` (`alwaysApply: true`); обновлён `qa-assistant-process`; Issue [#5](https://github.com/Sintik1/Qa_Asistant/issues/5).

### Промпт: Stage 6 — frontend MVP (prompt_templates §1)

**Запрос:** Senior Frontend Engineer; реализовать `user_stories.md` без бэкенда; React+TS+Tailwind; mock; без сторонних библиотек; не коммитить без согласования; проверить 3 раза.

**Результат:**
- M1: валидация PDF/DOCX/DOC/MD + превью имени/размера
- M2: mock-генерация + прогресс «Извлечение текста.» / «Генерация тест-кейсов...»
- M3: CSV UTF-8 BOM, имя `test_cases_YYYYMMDD_HHMMSS.csv`
- S1: параметры чанкинга + перегенерация
- S2: минимальный OOXML DOCX без библиотек
- S3: Notification API при длительности >30с и скрытой вкладке
- Issue [#6](https://github.com/Sintik1/Qa_Asistant/issues/6); код локально, коммит — после OK пользователя

---

### Промпт: Stage 7 — Docker

**Запрос:** упаковать приложение в Docker-контейнер для локального запуска.

**Результат:**
- `qa-assistant/Dockerfile` (multi-stage: Node build + nginx)
- `qa-assistant/nginx.conf` (SPA fallback)
- корневой `docker-compose.yml` → http://localhost:8080
- Issue [#7](https://github.com/Sintik1/Qa_Asistant/issues/7)

---

### Промпт: Stage 8 — README запуск

**Запрос:** добавить в README.md информацию по запуску приложения.

**Результат:**
- корневой `README.md` (Docker + npm + проверка UI)
- обновлён `qa-assistant/README.md`
- Issue [#8](https://github.com/Sintik1/Qa_Asistant/issues/8)

---

### Промпт: Stage 9 — chrome-devtools bug hunt

**Запрос:** протестировать приложение через chrome-devtools-mcp на баги; ответить сколько критичных и где.

**Результат:**
- `user-chrome-devtools` MCP: discovery error / auth timeout → fallback CDP через `cursor-ide-browser`
- Прогон: http://localhost:5173 и http://localhost:8080
- Happy-path OK: upload → token → generate → CSV/DOCX; негативы `empty`/`fail`/`corrupt`/zero-byte OK
- **Критических (P0): 0**
- High: имя CSV ≠ UI; `prompt`/`taskName`/шаблоны не влияют на генерацию; stale `generation.error`; мёртвые кнопки ManagementCard
- Issue [#9](https://github.com/Sintik1/Qa_Asistant/issues/9)

---

### Промпт: Stage 10 — тесты (prompt_templates §5)

**Запрос:** Senior Automation QA; pytest/Selenium; unit+API+UI; Page Object, Fluent API, parametrize; XSS/SQLi; без flaky; формат: сценарии → файлы → моки; вердикт пользователя обязателен.

**Результат:**
- Unit Vitest: 53 теста (бизнес-utils + security sanitization) — `npm test` green
- UI/Security: `tests/` (pytest + Selenium, Page Object + Fluent API)
- Адаптация: RestAssured/JUnit отброшены (не Java); API = mock + ERROR_MESSAGES
- Issue [#10](https://github.com/Sintik1/Qa_Asistant/issues/10); коммит — после вердикта

---

### Промпт: Stage 11 — AI debugging (screenshots + console)

**Запрос:** применить техники отладки с AI — мультимодальный анализ скриншотов багов; AI-интерпретация ошибок консоли.

**Результат:**
- Скриншоты: `uploads/debug/ai-debug/screenshots/` (invalid format, API fail, success, upload)
- Консоль приложения: uncaught errors **не найдены**; UI-ошибки живут в React state
- Артефакт: `SyntaxError: import.meta` — только от debug `Runtime.evaluate`, не от app
- Баги подтверждены визуально+DOM: CSV name mismatch, stale error, dual «Файл не выбран», Settings copy UX, dead ManagementCard, mock ignores prompt
- Issue [#11](https://github.com/Sintik1/Qa_Asistant/issues/11)

---

### Промпт: Stage 12 — fix bugs from AI debug

**Запрос:** `фиксируй` (B1–B7).

**Результат:**
- B3: CSV download → `Тест кейсы_<название>.csv` (`resolveDownloadCsvFileName` + `buildCsvFileName`)
- B4: смена requirements-файла вызывает `generation.clearError()`
- B1/B2: `FileUploadField` — без дубля empty-текста; reset `input.value` после reject
- B5: `MISSING_TOKEN_ON_SETTINGS` на Settings
- B6: ManagementCard buttons disabled + hint
- B7: mock учитывает `taskName` / `prompt`
- Vitest **56/56** green; `npm run build` OK
- Issue [#12](https://github.com/Sintik1/Qa_Asistant/issues/12)

### Промпт: тест адаптивной вёрстки на эмуляторах (шаг 14)

**Запрос:** senior QA — протестировать адаптив на мобильных/эмуляторах, выдать отчёт с багами.

**Результат:**
- Issue [#14](https://github.com/Sintik1/Qa_Asistant/issues/14)
- Матрица: 320 / 375 / 393 / 430 / 667×375 / 768 / 1024×768 / 1280 / 1440
- P0 layout — 0; R1 medium (touch «настройки» 14px); R2 low (input/select ~38px)
- Cards (&lt;md) / table (≥md) подтверждены на реальной mock-генерации

### Промпт: правь R1/R2 + полный регресс (шаг 15)

**Запрос:** исправить найденные баги и провести полное регрессионное тестирование.

**Результат:**
- Issue [#15](https://github.com/Sintik1/Qa_Asistant/issues/15)
- R1/R2: `min-h-11` на Link/ErrorMessage/form controls; touch CSS для `main a`
- Vitest 58/58; build OK
- Регресс: token/generate/cards/table/negatives/overflow 320–1440 — all PASS; новых багов нет
- Отчёт вынесен в `docs/TESTING_REPORT.md`; ссылки добавлены в корневой / `tests/` / `qa-assistant` README

---

### Промпт: библиотека промптов и шаблонов (варианты до кода)

**Запрос:** Senior Python Developer; на странице написания тест-кейсов нельзя добавить промпт и шаблон; сначала варианты (таблицы, локальное хранение или иное); три проверки, что ответ не ломает генерацию.

**Результат:**
- Выбран вариант A. Кнопки на http://127.0.0.1:5173/ сохраняют промпт и шаблон в таблицы пользователя.
- «Использовать» у промпта заполняет поле. У шаблона текст уходит в generate только для этого прогона и дописывается после примеров RAG.
- Пустой выбор не добавляет `template_text`. Библиотека не пишется в `case_chunks`.
- Issue [#55](https://github.com/Sintik1/Qa_Asistant/issues/55).

---

### Промпт: обновить отправку в Leopold на chatMulti

**Запрос:** сменить тело запроса на `api/1.0/lleopold/chatMulti`, но оставить параметры, которые приложение уже подставляет. Сначала варианты, три проверки, код не ломать.

**Результат ([#57](https://github.com/Sintik1/Qa_Asistant/issues/57)):**
- Живой клиент — `integrations/leopold_native.py`. Ollama шлёт другой JSON и не затрагивается
- Подставляются `model`, `system_prompt`, текст в `contents[0].text` и `chat_history[0].content`, `temperature` (сейчас 0.2)
- Пример API содержит заглушки (`"string"`, `fileSize` = max int, промпт «Сайга», `user_message: "Hi"`, `max_new_tokens: 1536`). Их нельзя копировать
- Выбран вариант B: `user_message` и пустые файловые поля, лимит токенов 15000, модель по умолчанию `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `LEOPOLD_API_URL` на этом стенде: `https://ai.rt.ru/api/1.0/lleopold/chatMulti`

---

### Промпт: один скрипт вместо двух терминалов

**Запрос:** запускать Flask и интерфейс одной командой вида `python run.py`.

**Результат ([#58](https://github.com/Sintik1/Qa_Asistant/issues/58)):**
- `run.py` в корне поднимает Flask на `127.0.0.1:5001` и Vite на `127.0.0.1:5173`
- Интерпретатор берётся из `.venv`. Ctrl+C останавливает оба процесса
- Зависимости скрипт не ставит: один раз `pip install -r requirements.txt` и `npm install`
- Pytest `tests/test_run_local.py` — 4 passed. Живые серверы тестом не запускались

---

## 4. Проблемы и решения

| Проблема | Решение |
|----------|---------|
| MCP `issue_write` без кнопки Submit | Issue через `~/.local/bin/gh issue create` ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)) |
| Auto-index AI cases в RAG отравляет few-shot | Убран auto после generate; только `POST /api/rag/index-cases` / templates ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)) |
| Live upload + `AUTH_DEV_BYPASS` → RLS 401 на `documents` | Нет `SUPABASE_SERVICE_ROLE_KEY` в `.env` → anon; smoke с JWT demo.reviewer |
| Leopold `API_EMPTY` ломал live generate | Smoke: Ollama 1.5b; fallback seed `test_cases` + `index-cases` |
| DOCX таблицы отрывались от разделов | Extract в порядке body; Heading→`##` для парсера |
| ТЗ без `3.1`, только Heading 2/3/4 | Hybrid parser: Word styles + явная нумерация |
| pgvector `<=>` в schema `extensions` | RPC `set search_path = public, extensions` |
| Node.js не установлен; Homebrew на macOS 13 не поставил Node | Бинарник Node v22.19.0 в `~/.local/node` |
| `gh` CLI отсутствовал | Бинарник `gh` 2.76.2; push через HTTPS + token |
| Figma MCP auth / namespace | `mcp_auth` → повторный discovery |
| Макет Figma — flat PNG | Структура из screenshot + ТЗ; reference PNG в repo |
| `.cursorrules` Flask vs задача React | По 1A — только frontend |
| П. 10–11 не велись с шага 1 | Issues + отчёт; далее — на каждом шаге |
| П. 10–11 были короткими и легко пропускались | Вынесены в ALWAYS + Cursor rule `alwaysApply: true` + чеклист |
| DOCX без сторонних библиотек | Минимальный ZIP(store)+OOXML вручную в `docxExport.ts` |
| Нужны негативные сценарии без API | Маркеры в имени файла: `empty`/`fail`/`corrupt`/`slow` |
| Имя compose-проекта из папки `ДЗ` пустое/невалидное | Явный `name: qa-assistant` в `docker-compose.yml` |
| chrome-devtools MCP недоступен (`spawn npx ENOENT`) | В `~/.cursor/mcp.json`: absolute `npx` + `PATH=~/.local/node/bin`; Reload MCP в Cursor |
| UI обещает `Тест кейсы_<название>.csv`, скачивается `test_cases_*.csv` | Зафиксировано в [#9](https://github.com/Sintik1/Qa_Asistant/issues/9); `buildCsvFileName` не подключён |
| После fail ошибка остаётся при выборе нового файла | `generation.clearError()` не вызывается из `useFileUpload` / смены файла |
| Vitest 3 vs Vite 8: конфликт типов `defineConfig` | Отдельный `vitest.config.ts`; `vite.config.ts` без `test` |
| Шаблон §5 тянет Java (RestAssured/JUnit) | Заменены на Vitest + pytest/Selenium под реальный стек |
| Заявление «100% покрытие всего приложения» | Покрыта бизнес-логика utils (unit) + ключевые UI-сценарии (E2E); не каждый JSX-line |
| `DOM.setFileInputFiles` запрещён в browser CDP | Upload через `DataTransfer` + `change` event в `Runtime.evaluate` |
| chrome-devtools MCP `list_pages` пустой | Fallback: cursor-ide-browser + CDP hooks |
| Console «тишина» при видимых UI-ошибках | Ошибки ТЗ идут в `role=alert`, не в `console.error` — для AI-отладки нужен DOM+скрин, не только console |
| CSV hint vs download name (B3) | `downloadCsv` переведён на `buildCsvFileName` |
| Stale generation.error (B4) | `handleRequirementsChange` → `clearError()` |
| Dual «Файл не выбран» + stale native name (B1/B2) | preview только при selectedFile; `input.value=''` при reject |
| Таблица тест-кейсов ломает узкие экраны | &lt; md — карточки; md+ — таблица в `.app-table-scroll` |
| Нужны именно media queries, не только Tailwind | CSS custom properties + `@media` в `index.css`, синхрон с `BREAKPOINTS` |
| chrome-devtools `take_screenshot` timeout | Опора на `evaluate_script` метрики + cursor-ide-browser screenshots |
| Inline link «настройки» 14px по высоте | Зафиксировано R1 в [#14](https://github.com/Sintik1/Qa_Asistant/issues/14); увеличен hit-area (`min-h-11` + inline-flex) в [#15](https://github.com/Sintik1/Qa_Asistant/issues/15) |
| `body { overflow-x: hidden }` маскирует scrollWidth | Аудит по `getBoundingClientRect` right &gt; vw (элементы не вылезали) |
| Form controls 37–42px на mobile | R2: `min-h-11` на input/select (TaskName, ProjectSelect, Settings, Chunk) |
| Дубли Tailwind input class / blob download / fill+send_keys | Stage 16: shared helpers без смены публичного API |
| Риск «сломать e2e» при рефакторе UI | DOM ids, тексты кнопок, ERROR_MESSAGES, mock markers сохранены |
| Resize thrash на результатах генерации | Stage 17: убрать JS breakpoint → CSS media dual view |
| Широкий `transition` / pulse / gradient paint | Stage 17: `transition-colors`, CSS progress, shared `.app-gradient` |
| Tailwind `md:hidden` vs custom `display: grid` | Stage 17 P17-1: переключение только в `index.css` `@media` |
| Selenium `localStorage.clear()` до navigation | SecurityError / flaky: сначала `open_home()`, потом clear |
| oxlint `react/set-state-in-effect` в `useMediaQuery` | `useSyncExternalStore` вместо `useState`+`useEffect` |
| Vitest 3.2.7: 2 moderate (`@vitest/mocker` path traversal) | Upgrade to Vitest **4.1.11** → audit 0 |
| npm arborist `edgesOut` на peer set Vitest 4/5 | Clean install + `--legacy-peer-deps` |
| Vitest 4 removed `environmentMatchGlobs` | Единый `environment: 'jsdom'` (+ RTL cleanup в setup) |
| Схема БД: риск over-engineering под learning JSON | Шаг 1: три варианта A/B/C; SQL только после выбора ([#20](https://github.com/Sintik1/Qa_Asistant/issues/20)) |
| Токен Leopold в таблице vs ТЗ «только .env» | В схемах — `has_api_token` / Vault; plaintext token не в Postgres |
| Self-hosted потребовал бы переписать Auth/RLS/Storage | Шаг 2: выбран Supabase; VPS не готовим ([#21](https://github.com/Sintik1/Qa_Asistant/issues/21)) |
| MCP не сразу в каталоге tools | Namespace `user-supabase` + `mcp_auth` |
| Advisors: search_path / SECURITY DEFINER RPC | `harden_auth_triggers` + revoke EXECUTE |
| MCP `issue_write` UI без кнопки Submit | Создать Issue через `curl` + `GITHUB_TOKEN` (REST API) |
| Flask Auth stub принимает `X-User-Id` без JWT | Шаг 5: verify Supabase JWT; header только в tests / `AUTH_DEV_BYPASS` |
| Storage: нет update/delete на debug, update на exports | Migration `security_storage_policies` |
| MCP `issue_write` без кнопки Submit | Шаг 6: `~/.local/bin/gh issue create` → [#26](https://github.com/Sintik1/Qa_Asistant/issues/26) |
| Нет `/generate` и multipart upload на Flask | В proposal: вариант B добавляет thin generate; A оставляет mock |
| `caplog` пуст при `propagate=False` у app logger | Тест вешает in-memory Handler на `qa_assistant` |
| npm не в PATH агента | `/Users/vlad/.local/node/bin` для Vitest |
| MCP `issue_write` без Submit на шаге 8 | `#29` через `~/.local/bin/gh issue create` |
| Исполнение Full QA до согласования методики | Gate: методика → OK пользователя → тесты → автотесты |
| macOS AirTunes занимает `:5000` | Flask на **5001**; `VITE_API_BASE_URL=http://127.0.0.1:5001` |
| CORS только `localhost:5173`, UI на `127.0.0.1` | Добавить `127.0.0.1:5173` / `:8080` в `CORS_ORIGINS` |
| Process env `VITE_API_BASE_URL` перекрывает `.env.local` | `env -u VITE_API_BASE_URL` при старте Vite |
| FE без JWT + `AUTH_DEV_BYPASS` без `X-User-Id` → 401 | Default local user id при bypass |
| `/auth` внутри `AppLayout` показывал вкладки Home/Settings | Отдельный `AuthLayout`; nav только после login ([#30](https://github.com/Sintik1/Qa_Asistant/issues/30)) |
| Flask CRUD не писал в Supabase (0 rows) | PostgREST repos + user JWT/RLS ([#31](https://github.com/Sintik1/Qa_Asistant/issues/31)) |
| Email confirm блокировал login после signup | Confirm SQL/admin или отключить Confirm email локально |
| Enum mismatch (`extracted`/`completed` vs `parsed`/`done`) | Mapping в `supabase_store` |
| README всё ещё описывал «только mock frontend» | Шаг 9: переписан под FE+Flask+Supabase + ссылка на `backend_documentation.md` ([#33](https://github.com/Sintik1/Qa_Asistant/issues/33)) |
| Signup rate-limit / invalid email для демо | SQL seed `auth.users` + `scripts/ensure_demo_reviewer.sql` ([#35](https://github.com/Sintik1/Qa_Asistant/issues/35)) |
| `AUTH_DEV_BYPASS` мог утечь на Railway | Игнор при PaaS markers / `PUBLIC_DEPLOY` / production ([#35](https://github.com/Sintik1/Qa_Asistant/issues/35)) |
| MCP `issue_write` без Submit (CI/CD ДЗ шаг 0) | `#37` через `~/.local/bin/gh issue create` ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Метрика без счётчика ломала бы CI/local | No-op без `VITE_YANDEX_METRIKA_ID`; id только public ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)) |
| `getSettings` 401 гасил `apiReady` при живом AI | Settings optional; health.ai.configured + live re-check before generate ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)) |
| MCP `issue_write` Create показывает форму без UI Submit | Шаг 6: комментарий в эпик [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) + код/docs |
| Google OAuth live `redirect_uri_mismatch` | Документирован §4.1 `OAUTH_SETUP.md`; добавить URI в Cloud Console ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Bypass pytest бил real Supabase → ProxyError 500 | `PERSIST_BACKEND=memory` в `bypass_client` ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Pages deploy skipped: CI fail on `npm audit` (`source-map-js` GHSA-68fv-2mgg-jv7q) | Override `source-map-js@1.2.2`; Pages Source=Actions + Variables via browser (gh token invalid) ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Google `redirect_uri_mismatch` на Flask callback | Перенос Google на Supabase Auth Provider; Console URI = `…supabase.co/auth/v1/callback` ([#40](https://github.com/Sintik1/Qa_Asistant/issues/40)) |
| Hybrid B: Cloudflare Tunnel 5xx / Clash fake-IP DNS `198.18.0.2` | Serveo SSH reverse tunnel к Flask; Ollama остаётся на localhost ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Ollama SIGTRAP в sandbox / Metal discover | Запуск вне sandbox + `OLLAMA_LLM_LIBRARY=cpu`, без HTTP_PROXY ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| Pages deploy blocked: ruff format `oauth_routes.py` | `ruff format`; deploy `if` + `workflow_dispatch` ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)) |
| MCP Issue Submit UI не виден | Подтверждение в чате + комментарий в [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) |
| `gh` не в PATH агента | Issue [#42](https://github.com/Sintik1/Qa_Asistant/issues/42) через `~/.local/bin/gh issue create` |
| MCP `issue_write` снова без Submit | [#43](https://github.com/Sintik1/Qa_Asistant/issues/43) через `~/.local/bin/gh` после «подтверждаю» |
| Chat искал только требования, пустой индекс кейсов давал «не найдено» | Retrieve docs + cases; `include_cases` ([#43](https://github.com/Sintik1/Qa_Asistant/issues/43)) |
| `/auth` → Failed to fetch | Clash fake-IP `240.x` на `supabase.co`; DIRECT `DOMAIN-SUFFIX,supabase.co` ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)) |
| Auth всё ещё мёртвый после Clash-диагноза | Free-проект **paused** → DNS снят; нужен Resume + keepalive ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)) |
| live_api_full_qa падает на ReadTimeout после AI 502 | Ollama down; следующий POST documents 30s → 503 PostgREST ([#45](https://github.com/Sintik1/Qa_Asistant/issues/45)) |
| Selenium ERROR webdriver_manager | Не в venv; CI эти тесты и так exclude ([#45](https://github.com/Sintik1/Qa_Asistant/issues/45)) |
| Selenium generate 120s timeout | Нет кнопки «Скачать CSV»; Chrome потом InvalidSessionId ([#46](https://github.com/Sintik1/Qa_Asistant/issues/46)) |
| Selenium в sandbox Cursor | Chrome exited / Selenium Manager без сети к chrome-for-testing ([#46](https://github.com/Sintik1/Qa_Asistant/issues/46)) |
| Leopold в этом репо слал OpenAI `/v1/chat/completions`, TestSites — другой JSON | Отдельный `LeopoldNativeClient`; Ollama не переведён на этот payload ([#47](https://github.com/Sintik1/Qa_Asistant/issues/47)) |
| Pipe-таблицы DOCX модель режет по строкам | Extract как в TestSites: один `TABLE_N_*` блок на таблицу ([#47](https://github.com/Sintik1/Qa_Asistant/issues/47)) |
| `has_table` в RAG видел только `\|` | Индекс считает таблицей и маркеры `TABLE_` ([#48](https://github.com/Sintik1/Qa_Asistant/issues/48)) |
| `npm` не в PATH песочницы | Vitest через `/Users/vlad/.local/node/bin` ([#48](https://github.com/Sintik1/Qa_Asistant/issues/48)) |
| Leopold и Ollama делят `QA_ASISTANT_MODEL` | Тег `qwen2.5:1.5b` без `/` не подставляется в Leopold ([#50](https://github.com/Sintik1/Qa_Asistant/issues/50)) |
| Вопрос про Домофон отвечает про роутер | Hash-вектор не про смысл; лексический отбор фрагментов ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)) |
| Вопрос про активатор и SDP отвечает страницей Домофон | Сравнение букв в коде путало «активна» и «активатор». Поиск переведён на эмбеддинги, ответ пишет модель ([#52](https://github.com/Sintik1/Qa_Asistant/issues/52)) |
| Модель с температурой по умолчанию выдумывает шаги | Чат отвечает с температурой 0. Если цитаты нет, показывается страница, которую модель назвала ([#52](https://github.com/Sintik1/Qa_Asistant/issues/52)) |
| Ответ про активатор не таблица, снизу требования всех страниц | Таблица Confluence хранится строками Markdown и рисуется таблицей. Под ответом остаётся только выбранная страница ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)) |
| Страница «Лицей» в чате одним абзацем | Чат склеивал соседние строки. Теперь каждая строка страницы — отдельный абзац, пустой абзац Confluence даёт отступ ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)) |
| Вопрос про Домофон и заявку на ТО отвечает только Домофоном | Код оставлял одну страницу. Теперь в ответ входят все страницы, пока сходство не проседает больше чем на 0.02 ([#54](https://github.com/Sintik1/Qa_Asistant/issues/54)) |
| «Добавить промт / шаблон» недоступны | Карточки без обработчиков. Хранение не выбрано: общий JSON смешает пользователей, `case_chunks` изменит каждую генерацию ([#55](https://github.com/Sintik1/Qa_Asistant/issues/55)) |
| Файл требований не заменяет `*Тут текст требований*` | Сначала файл не читался. После правки `POST /api/library/extract-text` отвечал 422, если текст длиннее 20 000 — лимит шаблона библиотеки ([#56](https://github.com/Sintik1/Qa_Asistant/issues/56)) |
| Генерация показывает «не удалось подключиться» | Файл уже прочитан. `POST /api/runs/…/generate` ждал Ollama `qwen2.5:1.5b` 491 с и вернул `API_UNAVAILABLE`: лимит ответа 300 с. Ollama при этом запущена ([#56](https://github.com/Sintik1/Qa_Asistant/issues/56)) |
| Пример `chatMulti` затирает промпт и режет CSV | Не копировать заглушки. `user_message` = наш текст, `max_new_tokens` остаётся 15000, модель из настроек ([#57](https://github.com/Sintik1/Qa_Asistant/issues/57)) |
| Два терминала легко забыть при переносе на другой ПК | `python run.py` из корня после venv и `npm install` ([#58](https://github.com/Sintik1/Qa_Asistant/issues/58)) |

---

## 5. Выводы и рекомендации

0z. Flask и Vite поднимаются одной командой `python run.py` из корня. Скрипт сам берёт `.venv`, порты 5001 и 5173, и по Ctrl+C останавливает оба процесса. Зависимости он не ставит ([#58](https://github.com/Sintik1/Qa_Asistant/issues/58)).
0y. Leopold ходит в `chatMulti` моделью `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`. Системный промпт, текст требований и лимит 15000 токенов остаются в теле. Заглушки примера (`Сайга`, `Hi`, `string`, 1536, огромный `fileSize`) не отправляются. Промпт из поля UI попадает в user-часть запроса как `Доп. промпт`, не в `system_prompt` ([#57](https://github.com/Sintik1/Qa_Asistant/issues/57)).
0x. Маркер `*Тут текст требований*` заменяется разобранным текстом файла, даже если документ длиннее 20 000 символов. Этот лимит остаётся только у сохранённого промпта и шаблона. Промпт без маркера не меняется ([#56](https://github.com/Sintik1/Qa_Asistant/issues/56)).
0w. Библиотека промптов и шаблонов — отдельные таблицы на пользователя. Выбранный текст добавляется к прогону. Пока ничего не выбрано, generate остаётся прежним. В `case_chunks` библиотеку не класть ([#55](https://github.com/Sintik1/Qa_Asistant/issues/55)).
0t. Какую страницу показать, решает вектор ближайших страниц и модель ответа. Список слов в коде для этого не используется. Ответ чата идёт с температурой 0; пустое название страницы заменяется её текстом ([#52](https://github.com/Sintik1/Qa_Asistant/issues/52)).
0u. Таблица страницы Confluence рисуется таблицей. Соседние абзацы страницы остаются отдельными строками ([#53](https://github.com/Sintik1/Qa_Asistant/issues/53)).
0v. В ответ попадают все страницы одной полосы сходства. Названия страниц для этого в коде не перечислены ([#54](https://github.com/Sintik1/Qa_Asistant/issues/54)).
0s. Страница Confluence сохраняется как Markdown (заголовки, нумерованные списки, выделение) и так же рисуется в чате ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)).
0r. Ответ чата — дословный текст найденного фрагмента. Локальная модель его не пересказывает ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)).
0q. При `hash`-эмбеддингах чат сначала оставляет фрагменты со словами вопроса. Иначе страница Confluence проигрывает случайному вектору ([#51](https://github.com/Sintik1/Qa_Asistant/issues/51)).
0p. Чат и генерация переключаются кнопками «Локально» / «Leopold» без смены эмбеддингов. Сейчас стенд на локальной Ollama `qwen2.5:1.5b` ([#50](https://github.com/Sintik1/Qa_Asistant/issues/50)).
0o. Confluence — ещё один источник тех же `document_chunks`, не второй поиск. Живой обход ждёт токен в `.env`; вложения и общий командный индекс не делались ([#49](https://github.com/Sintik1/Qa_Asistant/issues/49)).
0n. Автотесты нового парсинга и RAG не ходят в сеть: Leopold и чат мокаются; UI RAG — Vitest `ChatPage`, не только бэкенд ([#48](https://github.com/Sintik1/Qa_Asistant/issues/48)).
0m. Парсинг и Leopold из TestSites встраиваются в текущий upload/generate: маркеры таблиц + нативный payload. Весь `app.py` того проекта (обучение, assessment) не переносится. OLE `.doc` по-прежнему `CORRUPT_FILE` ([#47](https://github.com/Sintik1/Qa_Asistant/issues/47)).
0l. UI: Vitest полностью зелёный (92); Selenium happy-path generate зависит от живого JWT+AI, не от Page Object ([#46](https://github.com/Sintik1/Qa_Asistant/issues/46)).
0k. Полный QA: hermetic CI-слой зелёный; live generate/chat на этом Mac требуют Ollama + user JWT, не bypass UUID ([#45](https://github.com/Sintik1/Qa_Asistant/issues/45)).
0j. Free Supabase pause снимает DNS: без Resume вход всегда `Failed to fetch`; keepalive 2×/нед. ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)).
0i. Локальный логин Supabase ломается на Clash TUN fake-IP так же, как туннели: сначала DNS/TLS, не форма пароля ([#44](https://github.com/Sintik1/Qa_Asistant/issues/44)).
0h. RAG-чат: вопрос всегда сначала ищет чанки в БД, модель не отвечает «из головы» без retrieve; UI `/chat` показывает источники ([#43](https://github.com/Sintik1/Qa_Asistant/issues/43)).
0g. Hybrid B: при Clash fake-IP не полагаться на Cloudflare quick tunnel — Serveo/Pinggy; AI-туннель не нужен, если Flask на том же Mac ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0. CI/CD ДЗ: отдельный артефакт `cicd_integrations_documentation.md` + rule; решения G1–G9 до кода; OAuth предпочтительно через Supabase Providers; платежи — optional gate ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0a. Аналитика: Яндекс.Метрика через тонкий wrapper + SPA `hit`; цели как JS events; Webvisor off по умолчанию ([#41](https://github.com/Sintik1/Qa_Asistant/issues/41)).
0c. Мониторинг при G2=C: усиленный `/api/health` + local `watch_health.py`; UptimeRobot — когда появится публичный URL ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0d. Логирование: scenario prompts + redact до AI; централизация при G2=C = local rotating file ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0e. Шаг 8: integrations QA matrix + apply AI perf (code-split, hermetic tests, API_UNAVAILABLE mapping); Google OAuth needs Console redirect URI ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0f. Шаг 9: файлы сдачи `integration_documentation.md` + `security_audit.md`; формат п.1–4 закрыт локальным стендом при G2=C ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
0b. RAG: индекс leaf-секций в pgvector; generate не заменять top-k — только обогащать prompt (style + multi-doc); chat — отдельный retrieve. Embeddings: Ollama `nomic-embed-text` или `hash` для тестов ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)).
1. Gate согласования сохранять.
2. Для pixel-perfect лучше компонентные frames в Figma, не один screenshot.
3. Issues + `development_report.md` обновлять сразу при закрытии шага.
4. Перед детальной вёрсткой: Figma MCP auth + skill `figma-design-to-code`.
5. Skills покрывают весь цикл: UI, API, backend, data, тесты, процесс.
6. Следующая работа: pixel-perfect HomePage и/или каркас Flask-backend.
7. Трекинг стадий теперь enforced через ALWAYS-секцию и `alwaysApply` rule — не полагаться только на краткий пункт в середине файла.
8. Stage 6: mock-фронт закрывает happy-path и основные ошибки ТЗ; реальный extract/AI — только после бэкенда.
9. Stage 6 закоммичен после явного «ок фиксируй» пользователя.
10. Для демо без Node: `docker compose up --build` → http://localhost:8080 (нужен запущенный Docker Desktop).
11. Stage 9: P0-блокеров нет; чинить в первую очередь расхождение имени CSV с UI и очистку ошибки при смене файла.
12. Stage 10: unit-тесты гонять в CI сразу; Selenium — после поднятого `npm run dev` / Docker; вердикт пользователя — gate перед коммитом.
13. Stage 11: для UI-багов комбинировать скрин (мультимодалка) + a11y snapshot + CDP; console alone недостаточен, если ошибки только в state.
14. Stage 12: после AI-отладки сразу чинить high (CSV name, stale error), затем UX medium — меньше регрессий к демо.
15. Stage 13: держать breakpoints в одном источнике (`utils/breakpoints.ts` ↔ `index.css`); на phone предпочитать карточки широким таблицам.
16. Stage 14: адаптив готов к демо; перед polish — увеличить touch target у inline «настройки» и при желании у form controls.
17. Stage 15: после UI-фиксов всегда гонять короткий emulator-регресс (R1/R2 + generate + overflow) до commit.
18. Stage 16: рефактор по частям (styles → blob → hook → UI → PO); после — Vitest; commit только по явному OK.
19. Stage 17: layout perf — сначала CSS/DOM (без новых libs); JS media только если CSS нельзя; gate перед apply.
20. Stage 17: при CSS dual-view не смешивать Tailwind `hidden`/`md:hidden` с кастомным `display` того же узла — specificity/cascade ломает адаптив.
21. Stage 18: для origin-bound Storage в Selenium — всегда navigate first; media hooks — `useSyncExternalStore`; Vitest ≥4.1.11 закрывает mocker CVE.
22. Backend ДЗ шаг 1: сначала варианты схем и gate; SQL/миграции только после выбора A/B/C; рекомендация — **B Operational** (см. `backend_documentation.md` §1).
23. После выбора B: одна init-миграция с RLS и trigger signup; применение на живой Supabase — шаг 3 ДЗ.
24. Шаг 2: infra = Supabase; не смешивать с self-hosted без явной смены решения; следующий фокус — создать cloud-проект и `db push`.
25. Шаг 3: MCP к `revyywfeeqdmlgrbakpj` работает; схема в cloud; дальше API/Auth, не трогать prod schema без миграции.
26. Шаг 4: hybrid C + Qwen/Leopold; Flask memory repos для тестов; JWT→Supabase — на шаге 5.
27. Шаг 5: не писать свой Auth — схема уже на `auth.users`+RLS; JWT middleware + FE signup/login реализованы ([#25](https://github.com/Sintik1/Qa_Asistant/issues/25)); следующий — шаг 6 FE↔API с Bearer.
28. Шаг 6: Axios не нужен (`apiFetch` + Supabase); вариант **B** реализован — FE api/hooks + `POST …/generate` ([#26](https://github.com/Sintik1/Qa_Asistant/issues/26)); PDF extract на сервере — later.
29. Шаг 7: structured JSON logs + `request_id` + AI analyze (CLI/API); Supabase Logs через Dashboard/MCP, не дублировать в свою таблицу без нужды ([#27](https://github.com/Sintik1/Qa_Asistant/issues/27)).
30. Extract B: серверный parse обязателен для PDF/DOCX; legacy OLE `.doc` без LibreOffice → `CORRUPT_FILE` до отдельного конвертера ([#28](https://github.com/Sintik1/Qa_Asistant/issues/28)).
31. Шаг 8 Full QA: методика → OK → live/DevTools → фиксы → автотесты; на macOS избегать `:5000` (AirTunes) и синхронизировать CORS с origin (`localhost` vs `127.0.0.1`) ([#29](https://github.com/Sintik1/Qa_Asistant/issues/29)).
32. Persistence: не считать FE↔API интеграцию готовой, пока `persist!=supabase` и таблицы пустые; для signup нужен confirm email / service role ([#31](https://github.com/Sintik1/Qa_Asistant/issues/31)).
33. Сдача ДЗ: один вход — `backend_documentation.md` (архитектура/деплой/API/примеры) + README со стеком FE+BE; не оставлять в README формулировку «только mock» ([#33](https://github.com/Sintik1/Qa_Asistant/issues/33)).
34. Без бюджета на VPS: для проверяющего достаточно инструкций + FULL_QA + воспроизводимый локальный стенд; публичный URL не обязателен ([#34](https://github.com/Sintik1/Qa_Asistant/issues/34)).
35. Feedback: compose UI-only явно; демо-login + Table Editor checklist; `AUTH_DEV_BYPASS` hard-disable на PaaS; деплой/скринкаст — опция ([#35](https://github.com/Sintik1/Qa_Asistant/issues/35)).
36. RAG: pytest user-scenarios + `live_rag_smoke.py` (memory и Supabase JWT); для cloud live нужен JWT или `SUPABASE_SERVICE_ROLE_KEY`, не только bypass ([#36](https://github.com/Sintik1/Qa_Asistant/issues/36)).
37. CI/CD ДЗ: фиксировать в `cicd_integrations_documentation.md` + Issues; MCP Issue без Submit → `~/.local/bin/gh`; новые MCP только после OK ([#37](https://github.com/Sintik1/Qa_Asistant/issues/37)).
38. Стек описывать по манифестам и миграциям, не только по README: FE (Vite/React/TS/Tailwind), BE (Flask), BaaS (Supabase+pgvector), AI (Ollama/Leopold), CI (Actions+Pages) ([#42](https://github.com/Sintik1/Qa_Asistant/issues/42)).

---

## 6. Журнал стадий (Issues)

| Стадия | Issue | Статус |
|--------|-------|--------|
| Шаг 1 — Инициализация фронтенда | [#1](https://github.com/Sintik1/Qa_Asistant/issues/1) | completed (closed) |
| Шаг 2 — GitHub репозиторий | [#2](https://github.com/Sintik1/Qa_Asistant/issues/2) | completed (closed) |
| Шаг 3 — Структура UI (Figma + ТЗ) | [#3](https://github.com/Sintik1/Qa_Asistant/issues/3) | completed (closed) |
| Шаг 4 — Установка Skills | [#4](https://github.com/Sintik1/Qa_Asistant/issues/4) | completed (closed) |
| Шаг 5 — ALWAYS трекинг (Issues + отчёт) | [#5](https://github.com/Sintik1/Qa_Asistant/issues/5) | completed (closed) |
| Шаг 6 — Frontend MVP (mock M1–M3, S1–S3) | [#6](https://github.com/Sintik1/Qa_Asistant/issues/6) | completed (closed), commit `8a05e83` |
| Шаг 7 — Docker frontend | [#7](https://github.com/Sintik1/Qa_Asistant/issues/7) | completed (closed) |
| Шаг 8 — README: запуск приложения | [#8](https://github.com/Sintik1/Qa_Asistant/issues/8) | completed (closed) |
| Шаг 9 — Chrome DevTools / CDP bug hunt | [#9](https://github.com/Sintik1/Qa_Asistant/issues/9) | open (результат зафиксирован; закрытие после OK) |
| Шаг 10 — Автотесты (prompt_templates §5) | [#10](https://github.com/Sintik1/Qa_Asistant/issues/10) | completed locally (`e2f2e28`; push/close после OK) |
| Шаг 11 — AI screenshot + console debug | [#11](https://github.com/Sintik1/Qa_Asistant/issues/11) | open (результат в комментарии; закрытие после OK) |
| Шаг 12 — Fix B1–B7 | [#12](https://github.com/Sintik1/Qa_Asistant/issues/12) | open (ожидает вердикт/коммит) |
| Шаг 13 — Адаптив + media queries | [#13](https://github.com/Sintik1/Qa_Asistant/issues/13) | completed (closed), commit `8e46176` |
| Шаг 14 — Тест адаптивной вёрстки (эмуляторы) | [#14](https://github.com/Sintik1/Qa_Asistant/issues/14) | open (отчёт готов; R1/R2 → #15) |
| Шаг 15 — Fix R1/R2 + полный регресс | [#15](https://github.com/Sintik1/Qa_Asistant/issues/15) | completed (отчёт в `docs/TESTING_REPORT.md`; commit в этом цикле) |
| Шаг 16 — Behavior-preserving refactor | [#16](https://github.com/Sintik1/Qa_Asistant/issues/16) | completed, commit `6dc1eed` |
| Шаг 17 — Оптимизация вёрстки (perf) | [#17](https://github.com/Sintik1/Qa_Asistant/issues/17) | completed (closed), commits `69ace4a` / `45187c4` |
| Шаг 18 — Selenium + Vitest + RTL + docs | [#18](https://github.com/Sintik1/Qa_Asistant/issues/18) | completed, commit `53e1583` (close после OK) |
| Backend ДЗ — процесс + backend_documentation.md | [#19](https://github.com/Sintik1/Qa_Asistant/issues/19) | in progress |
| Backend ДЗ шаг 1 — проектирование БД (A/B/C) | [#20](https://github.com/Sintik1/Qa_Asistant/issues/20) | choice done → migration B |
| Backend ДЗ шаг 1 — миграция Variant B | [#20](https://github.com/Sintik1/Qa_Asistant/issues/20) | done (awaiting OK to close) |
| Backend ДЗ шаг 2 — infra Supabase vs VPS | [#21](https://github.com/Sintik1/Qa_Asistant/issues/21) | done (awaiting OK): **A Supabase** |
| Backend ДЗ шаг 3 — MCP + schema deploy | [#22](https://github.com/Sintik1/Qa_Asistant/issues/22) | done (awaiting OK): project live |
| Backend ДЗ шаг 4 — API варианты A/B/C | [#23](https://github.com/Sintik1/Qa_Asistant/issues/23) | choice → C |
| Backend ДЗ шаг 4 — Flask hybrid C + Qwen | [#23](https://github.com/Sintik1/Qa_Asistant/issues/23) | done (awaiting OK), pytest 8/8 |
| Ollama qwen2.5 7b/14b study mode | [#23](https://github.com/Sintik1/Qa_Asistant/issues/23) | done, pytest 15/15 |
| Тест API endpoints + Ollama live | [#24](https://github.com/Sintik1/Qa_Asistant/issues/24) | done: pytest 16/16, live 17/17 |
| Backend ДЗ шаг 5 — Auth / RLS / CORS / secrets | [#25](https://github.com/Sintik1/Qa_Asistant/issues/25) | done (awaiting OK): JWT + FE Auth + Storage RLS |
| Backend ДЗ шаг 6 — FE ↔ Backend API | [#26](https://github.com/Sintik1/Qa_Asistant/issues/26) | done (awaiting OK / commit); Backend ДЗ шаг 6 → `backend_documentation.md` §4.4 |
| Backend ДЗ шаг 7 — ошибки и логирование | [#27](https://github.com/Sintik1/Qa_Asistant/issues/27) | done (awaiting OK): вариант **B**; Backend ДЗ шаг 7 → `backend_documentation.md` §3.3.1 |
| Backend extract PDF/DOCX/DOC | [#28](https://github.com/Sintik1/Qa_Asistant/issues/28) | done (awaiting OK): вариант **B**; → `backend_documentation.md` §4.6 |
| Backend ДЗ шаг 8 — Full QA API+UI | [#29](https://github.com/Sintik1/Qa_Asistant/issues/29) | done (awaiting OK): live 23/23, UI PASS, pytest 59; → `backend_documentation.md` §6 |
| FE Auth enable (`VITE_SUPABASE_*`) | [#29](https://github.com/Sintik1/Qa_Asistant/issues/29) | done: `.env.local` + restart; `/auth` + RequireAuth |
| Auth layout без вкладок | [#30](https://github.com/Sintik1/Qa_Asistant/issues/30) | done (awaiting OK): `AuthLayout` + route split |
| DB persistence signup+happy path | [#31](https://github.com/Sintik1/Qa_Asistant/issues/31) | done (awaiting OK): Supabase repos; autonomous API+UI PASS; docs→`DB_PERSISTENCE_TEST_REPORT.md` |
| Единый отчёт Full QA | [#32](https://github.com/Sintik1/Qa_Asistant/issues/32) | done (awaiting OK): `docs/FULL_QA_REPORT.md` |
| Backend ДЗ шаг 9 — docs + README | [#33](https://github.com/Sintik1/Qa_Asistant/issues/33) | done (closed): `backend_documentation.md` + `README.md`; → §5.10 / §6 |
| README для проверяющего (без деплоя) | [#34](https://github.com/Sintik1/Qa_Asistant/issues/34) | done (closed): блок в корневом README |
| Reviewer feedback (demo + bypass) | [#35](https://github.com/Sintik1/Qa_Asistant/issues/35) | done (closed): demo/checklist/bypass + screencast; commit `ddd6fcf` |
| RAG + section parser (style/multi-doc/chat) | [#36](https://github.com/Sintik1/Qa_Asistant/issues/36) | done (awaiting OK): pgvector + Chat UI; guide → [`docs/RAG_USAGE.md`](docs/RAG_USAGE.md) |
| RAG verify + autotests (user scenarios) | [#36](https://github.com/Sintik1/Qa_Asistant/issues/36) | done (awaiting OK): pytest 31 / vitest 3 / live smoke PASS; → `backend_documentation.md` §5.11 |
| CI/CD + integrations ДЗ — workflow + docs | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | шаг 0 done (awaiting OK): G2=C CI-only; → `cicd_integrations_documentation.md` §0/§10 |
| CI/CD ДЗ шаг 1 — GitHub Actions | [#38](https://github.com/Sintik1/Qa_Asistant/issues/38) | done (awaiting OK): `ci.yml`; → §2 |
| CI/CD ДЗ шаг 2 — Security audit | [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) | done (awaiting OK): remediations landed; → `docs/SECURITY_AUDIT.md` |
| CI/CD ДЗ шаг 3 — OAuth2 Google+Yandex | [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) | done (awaiting OK): → `docs/OAUTH_SETUP.md` §4 |
| CI/CD ДЗ шаг 4 — Яндекс.Метрика | [#41](https://github.com/Sintik1/Qa_Asistant/issues/41) | done (awaiting OK): → `docs/METRIKA_SETUP.md` + `cicd_integrations_documentation.md` §5/§10 |
| CI/CD ДЗ шаг 6 — UptimeRobot + health | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): → `docs/UPTIME_SETUP.md` §7 (отдельная Issue UI недоступна) |
| CI/CD ДЗ шаг 7 — логирование | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): scenarios + redact; → `docs/LOGGING.md` + `cicd_integrations_documentation.md` §8/§10 |
| CI/CD ДЗ шаг 8 — integrations QA + perf | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): → `docs/INTEGRATIONS_QA_STEP8.md` + §10; pytest 121 / vitest 87 (`test_supabase_rest`, `AuthCallbackPage.test`) |
| CI/CD ДЗ шаг 9 — оформление сдачи | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): `integration_documentation.md` + `security_audit.md` + README; → §10 |
| Acceptance: G2=B Pages auto-deploy | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): deploy job → https://sintik1.github.io/Qa_Asistant/ |
| Pages one-time setup + audit unblock | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done: Pages+Variables; CI [run](https://github.com/Sintik1/Qa_Asistant/actions/runs/37422990061) green; site live; → `cicd_integrations_documentation.md` §10 |
| OAuth Google → Supabase Provider | [#40](https://github.com/Sintik1/Qa_Asistant/issues/40) | done (awaiting Console URI + smoke): Google Enabled; Redirect URLs×3; FE signInWithOAuth; → `docs/OAUTH_SETUP.md` §1 |
| Hybrid B: public FE+API, local AI | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done (awaiting OK): Serveo→Flask + Ollama local; `VITE_API_BASE_URL`; → `docs/HYBRID_LOCAL_AI.md` + `cicd_integrations_documentation.md` §10 |
| Hybrid B restart runbook | [#37](https://github.com/Sintik1/Qa_Asistant/issues/37) | done: пошаговый подъём после reboot → [`docs/HYBRID_B_RESTART.md`](docs/HYBRID_B_RESTART.md) |
| Инвентаризация технологий проекта | [#42](https://github.com/Sintik1/Qa_Asistant/issues/42) | done: сводка в чате по манифестам и docs |
| RAG project chat (retrieve → answer) | [#43](https://github.com/Sintik1/Qa_Asistant/issues/43) | done (awaiting OK): docs+cases retrieve; `/chat`; → `backend_documentation.md` §5.12 |
| Auth Failed to fetch (Clash DNS) | [#44](https://github.com/Sintik1/Qa_Asistant/issues/44) | done (awaiting DIRECT): supabase.co → 240.x; hint in UI; → `docs/OAUTH_SETUP.md` §3.1 |
| Unpause + keepalive so Auth stays up | [#44](https://github.com/Sintik1/Qa_Asistant/issues/44) | done (awaiting Dashboard Resume): paused NXDOMAIN; workflow + script |
| Full project QA run | [#45](https://github.com/Sintik1/Qa_Asistant/issues/45) | done (awaiting OK): pytest 124 / vitest 92; → `docs/FULL_QA_RUN_2026-11-23.md` |
| All UI tests (Vitest + Selenium) | [#46](https://github.com/Sintik1/Qa_Asistant/issues/46) | done (awaiting OK): vitest 92; selenium 11/13; → `docs/UI_TEST_RUN_2026-11-23.md` |
| Парсинг TestSites + нативный Leopold | [#47](https://github.com/Sintik1/Qa_Asistant/issues/47) | done (awaiting OK): `TABLE_*` + `LeopoldNativeClient`; pytest 35; → `backend_documentation.md` §5.13 |
| Тесты TABLE/Leopold + RAG UI | [#48](https://github.com/Sintik1/Qa_Asistant/issues/48) | done (awaiting OK): pytest 55, Vitest chat 9; `has_table` для `TABLE_` |
| RAG по пространству Confluence | [#49](https://github.com/Sintik1/Qa_Asistant/issues/49) | done (awaiting token): sync в `document_chunks`; кнопка в `/chat`; → `docs/RAG_USAGE.md` §3.5 |
| Переключатель Leopold ↔ Ollama | [#50](https://github.com/Sintik1/Qa_Asistant/issues/50) | done (awaiting OK): `PUT /api/ai/provider`; стенд на `ollama`; → `backend_documentation.md` §5.15 |
| Чат: страница по словам вопроса | [#51](https://github.com/Sintik1/Qa_Asistant/issues/51) | done (awaiting OK): дословный Markdown страницы в чате; → `backend_documentation.md` §5.16 |
| ИИ выбирает страницы пространства | [#52](https://github.com/Sintik1/Qa_Asistant/issues/52) | done (awaiting OK): `nomic-embed-text`, температура 0, цитата или текст названной страницы; живой SDP → активатор, Домофон → инструкция; → `backend_documentation.md` §5.17 |
| Таблица Confluence в чате | [#53](https://github.com/Sintik1/Qa_Asistant/issues/53) | done (awaiting OK): markdown-таблица и один источник под ответом; → `backend_documentation.md` §5.18 |
| Все страницы одного сходства | [#54](https://github.com/Sintik1/Qa_Asistant/issues/54) | done (awaiting OK): полоса 0.02, Домофон и заявка на ТО вместе; → `backend_documentation.md` §5.19 |
| Библиотека промптов и шаблонов | [#55](https://github.com/Sintik1/Qa_Asistant/issues/55) | done (awaiting OK): вариант A, таблицы `user_prompts` и `scenario_templates`; → `backend_documentation.md` §5.20 |
| Маркер требований в промпте | [#56](https://github.com/Sintik1/Qa_Asistant/issues/56) | done (awaiting OK): длинный файл читается; generate 502 — таймаут Ollama 300 с, не обрыв файла; → `backend_documentation.md` §5.21 |
| Leopold chatMulti | [#57](https://github.com/Sintik1/Qa_Asistant/issues/57) | done (awaiting OK): вариант B, Qwen3, `user_message`; → `backend_documentation.md` §5.22 |
| Один скрипт локального запуска | [#58](https://github.com/Sintik1/Qa_Asistant/issues/58) | done (awaiting OK): `python run.py`; → `backend_documentation.md` §2.4 |

---

## 7. Stage 4 details — установленные skills

### Application (project)

| Skill | Domain |
|-------|--------|
| `qa-assistant-ui` | Карта экранов / папок |
| `qa-assistant-react` | React/TS/Tailwind |
| `qa-assistant-backend` | Flask / pipeline |
| `qa-assistant-data` | Repository / UoW / SQL |
| `qa-assistant-api` | FE↔BE контракт |
| `qa-assistant-testing` | Pytest / quality |
| `qa-assistant-process` | Issues + отчёт (ALWAYS) |

### Figma (project)

`figma-design-to-code`, `figma-use`, `figma-implement-motion`, `figma-use-motion`, `figma-code-connect`, `figma-generate-design`

### Rules

- `.cursor/rules/process-tracking.mdc` — **alwaysApply: true** (§10–11)
- `.cursor/rules/backend-homework-dz.mdc` — **alwaysApply: true** (§12, backend ДЗ + все прочие rules)
- `.cursor/rules/cicd-integrations-dz.mdc` — **alwaysApply: true** (CI/CD + integrations ДЗ → `cicd_integrations_documentation.md`)
- `.cursor/rules/ui-figma-workflow.mdc`
- `.cursor/rules/backend-data-workflow.mdc`

### Personal mirror (машина)

`~/.cursor/skills/`: core Figma skills

### Как проверить

```bash
ls .cursor/skills
ls .cursor/rules
```

GitHub: https://github.com/Sintik1/Qa_Asistant/tree/main/.cursor
