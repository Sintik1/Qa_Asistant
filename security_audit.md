# Security Audit Report — QA Assistant

**Файл сдачи ДЗ:** `security_audit.md` (корень репозитория)  
**Дата аудита:** 2026-10-05 · **обновление remediations:** 2026-10-05–06  
**Issue:** [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) · Эпик [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
**Метод:** `npm audit`, `pip-audit`, ручной + AI-разбор кода (OWASP Top 10)  
**Статус:** remediations **применены** (A2 + B1a + B2a + B3a + B4b + B5b + C1 + C2)

Дубликат/расширенный журнал: [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md) · сводка в [`integration_documentation.md`](integration_documentation.md) §3 и [`cicd_integrations_documentation.md`](cicd_integrations_documentation.md) §3.

---

## 1. Список найденных уязвимостей

### 1.1. Зависимости

| Источник | Находка | Severity |
|----------|---------|----------|
| `pip-audit` | **flask-cors** 5.0.1 — PYSEC-2026-1383/1384/1385 | **High** |
| `pip-audit` | python-dotenv 1.2.1 — PYSEC-2026-2270 | Low–Med |
| `pip-audit` | pytest / click / anyio (transitive) | Low–Med |
| `npm audit` | 0 vulnerabilities (на момент аудита) | — |

### 1.2. Код / конфигурация (OWASP)

| ID | Риск | Severity | Статус |
|----|------|----------|--------|
| D1 | Устаревший flask-cors | High | **Исправлен** |
| C2 | Admin `analyze-logs` без обязательного admin token вне tests | Medium | **Исправлен** (B2a) |
| C1 | Нет security headers на Flask | Medium | **Исправлен** (B1a) |
| C3 | Legacy API token в `localStorage` | Low | **Исправлен** (B3a) |
| C4 | Нет `npm audit` / `pip-audit` в CI | Low | **Исправлен** (C1) |
| — | XSS / CSRF / SQLi | Low | OK (React escape; Bearer JWT; PostgREST) |
| — | `AUTH_DEV_BYPASS` | Info (local only) | Hard-disable на PaaS/prod |

---

## 2. Описание исправлений

| Пакет | Что сделано |
|-------|-------------|
| **A2** | `flask-cors>=6`; обновлены dotenv / click / anyio / pytest (CI Python 3.11) |
| **B1a** | Headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` |
| **B2a** | `LOG_ANALYZE_ADMIN_TOKEN` обязателен вне `TESTING` |
| **B3a** | Settings: секрет не пишется в `localStorage`; purge legacy key |
| **B4b / B5b** | Upload DoS / rate limit — отложены (согласовано) |
| **C1** | CI: `npm audit --audit-level=high`, `pip-audit -r requirements.txt` |
| **C2** | README → Security + этот отчёт |

Дополнительно (шаг 8): PostgREST transport errors → `API_UNAVAILABLE` 503; hermetic tests без live Supabase.

---

## 3. Рекомендации по безопасности

1. Секреты только в `.env` / GitHub Secrets / PaaS env — никогда в `VITE_*` (кроме публичного Metrika counter id).
2. Не включать `AUTH_DEV_BYPASS` на публичном хосте; для проверки — демо-аккаунт из README.
3. Google/Yandex OAuth: redirect URI побайтово совпадать с Console (`docs/OAUTH_SETUP.md` §4.1).
4. Периодически гонять `npm audit` / `pip-audit` (уже в CI).
5. При появлении публичного URL: HSTS на reverse-proxy; рассмотреть rate limit на upload/generate.
6. `LOG_ANALYZE_ADMIN_TOKEN` — уникальный; не коммитить; в prod можно `LOG_ANALYZE_ENABLED=0`.
7. Service role key — только сервер Flask; не отдавать во frontend.

---

## 4. Положительные практики (сохранять)

- JWT middleware + RLS на Supabase  
- Upload: whitelist расширений + size limit + `Path(filename).name`  
- CORS whitelist  
- JSON логи + redact перед AI-анализом  
- Deploy job в CI отключён при локальном AI (меньше attack surface публичного API)

---

_Последнее обновление: 2026-10-06 — шаг 9 оформления сдачи._
