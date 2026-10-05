# Security Audit Report — QA Assistant

**Дата:** 2026-10-05  
**Issue:** [#39](https://github.com/Sintik1/Qa_Asistant/issues/39) · Эпик [#37](https://github.com/Sintik1/Qa_Asistant/issues/37)  
**Метод:** `npm audit`, `pip-audit`, ручной + AI-разбор кода (OWASP Top 10)  
**Статус:** remediations **применены** (gate A2+B1a+B2a+B3a+B4b+B5b+C1+C2)

Сводка также в [`cicd_integrations_documentation.md`](../cicd_integrations_documentation.md) §3.

---

## 1. Executive summary

| Область | Вердикт |
|---------|---------|
| Frontend deps (`npm audit`) | **0** уязвимостей |
| Backend deps (`pip-audit`) | **8** CVE в **5** пакетах (критично обновить **flask-cors**) |
| Auth / JWT / RLS | В целом **хорошо** (Supabase JWT, bypass только local/test) |
| SQL injection | **Низкий риск** (PostgREST, без string-SQL) |
| XSS | **Низкий риск** (React text binding; нет `dangerouslySetInnerHTML`) |
| CSRF | **Низкий риск** (Bearer JWT, не cookie-session) |
| Прочее | Нет security headers; нет rate limit; admin analyze-logs слабо gated если нет admin token; legacy token в `localStorage` |

**Итог:** приложение в приемлемом состоянии для учебного стенда; обязательный минимум remediations — обновление зависимостей (особенно `flask-cors`) + точечные hardening (headers / admin gate / CI audit).

---

## 2. Dependency audit

### 2.1. Frontend — `npm audit` (qa-assistant/)

```
found 0 vulnerabilities
```

Prod + dev дерево: без critical/high/moderate/low на момент аудита.

### 2.2. Backend — `pip-audit -r requirements.txt`

| Package | Installed | Advisories | Fix | Severity (оценка) | Runtime? |
|---------|-----------|------------|-----|-------------------|----------|
| **flask-cors** | 5.0.1 | PYSEC-2026-1383, 1384, 1385 | **≥6.0.0** (доступен 6.0.5) | **High** | да |
| python-dotenv | 1.2.1 | PYSEC-2026-2270 | ≥1.2.2 | Low–Med | да |
| pytest | 8.4.2 | PYSEC-2026-1845 | ≥9.0.3 | Low (dev) | только тесты |
| click | 8.1.8 | PYSEC-2026-2132 | ≥8.3.3 | Low (transitive) | да (Flask CLI) |
| anyio | 4.12.1 | PYSEC-2026-4024, 4025 | ≥4.14.2 | Low–Med (transitive via httpx) | да |

`safety` CLI потребовал login — в отчёте не использован; `pip-audit` достаточен.

---

## 3. OWASP Top 10 — code review

| # | Риск | Наблюдение | Severity | Статус |
|---|------|------------|----------|--------|
| A01 | Broken Access Control | JWT на `/api/*` кроме health/ai ping; `AUTH_DEV_BYPASS` игнорируется на PaaS/prod; default `X-User-Id` только при bypass | Low (prod) / Info (local) | OK с оговоркой local |
| A01 | Admin surface | `POST /api/admin/analyze-logs`: при пустом `LOG_ANALYZE_ADMIN_TOKEN` достаточно обычного JWT пользователя | **Medium** | Needs fix (варианты ниже) |
| A02 | Crypto / secrets | Секреты в `.env`; anon key на FE — норма; service role только сервер | Low | OK |
| A03 | Injection (SQL) | Доступ через PostgREST params/JSON; string SQL запрещён rules | Low | OK |
| A03 | Path / upload | `Path(filename).name`; whitelist расширений; лимит 100 МБ | Low–Med (DoS memory) | Частично OK |
| A03 | XSS | Нет `dangerouslySetInnerHTML`; Chat/ошибки через text nodes React | Low | OK |
| A04 | Insecure design | Legacy Settings пишет «API token» в `localStorage` (mock-era); реальный AI token — server `.env` | Low | Cleanup recommended |
| A05 | Misconfiguration | Нет CSP / `X-Frame-Options` / `X-Content-Type-Options` / HSTS на Flask | **Medium** | Needs fix |
| A05 | CORS | Whitelist `CORS_ORIGINS`; `supports_credentials=True`; разрешены `X-User-Id` / `X-Skip-Auth` (для local) | Low–Med | OK + flask-cors upgrade |
| A06 | Vulnerable components | См. §2 — flask-cors устарел | **High** | Needs fix |
| A07 | Auth failures | JWT HS256 + aud `authenticated`; fallback Auth `/user` | Low | OK |
| A08 | Integrity | Нет `npm audit` / `pip-audit` в CI | Low | Needs fix (CI) |
| A09 | Logging | JSON access logs; analyze-logs может отправить хвост логов в AI | Info | Document + tighten admin |
| A10 | SSRF | AI/embedding URL из env, не из user input | Low | OK |

### CSRF / XSS / SQLi — вывод для ДЗ

| Атака | Оценка | Почему |
|-------|--------|--------|
| XSS | Защищены базово | React escaping; UI-тесты `test_security.py` (Selenium, вне CI) |
| CSRF | Низкий риск classic CSRF | API на `Authorization: Bearer`, не session cookie |
| SQL injection | Низкий риск | Нет raw SQL; PostgREST + RLS |

---

## 4. Положительные находки (не трогать без нужды)

- Hard-disable `AUTH_DEV_BYPASS` на production/PaaS markers (`app/__init__.py`)
- Единый JWT middleware + error JSON без stack traces клиенту
- Upload: extension whitelist + size limit (`core/doc_reader.py` / `core/messages.py`)
- Storage path: `Path(filename).name` (снижает path traversal)
- Secrets не в git (`.env.example` placeholders)

---

## 5. Предлагаемые варианты исправлений (gate)

### Пакет A — зависимости (рекомендуется **обязательно**)

1. Поднять `flask-cors` → `>=6.0,<7` в `requirements.txt`
2. Поднять `python-dotenv` → `>=1.2.2,<2`
3. Переустановить/зафиксировать transitive: `click`, `anyio` через обновление deps / pin lower-bounds
4. `pytest` → `>=9.0.3,<10` (dev; может потребовать мелких правок тестов — проверим)

**Вариант A1:** только runtime (flask-cors + dotenv + transitive)  
**Вариант A2:** A1 + pytest major bump  

### Пакет B — hardening кода

| ID | Предложение | Варианты |
|----|-------------|----------|
| B1 | Security headers after_request | **B1a** минимальный набор (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) · **B1b** + CSP report-only (осторожнее с Vite) |
| B2 | `/api/admin/analyze-logs` | **B2a** требовать `LOG_ANALYZE_ADMIN_TOKEN` всегда в non-testing · **B2b** ограничить роль/env `LOG_ANALYZE_ENABLED=0` по умолчанию в prod |
| B3 | Legacy `localStorage` API token UI | **B3a** убрать запись токена / оставить только `has_api_token` · **B3b** оставить + предупреждение в UI/docs |
| B4 | Upload DoS | **B4a** streaming/size check до полного `read()` · **B4b** оставить как есть (лимит 100 МБ уже есть) |
| B5 | Rate limiting | **B5a** простой in-memory limiter на upload/generate/auth-sensitive · **B5b** отложить (out of scope для локального стенда) |

### Пакет C — процесс / CI

| ID | Предложение |
|----|-------------|
| C1 | Job или step в GitHub Actions: `npm audit --audit-level=high` + `pip-audit -r requirements.txt` |
| C2 | Краткая секция в README «Security» со ссылкой на этот отчёт |

### Рекомендация агента (минимум для закрытия шага 2)

**A2 + B1a + B2a + B3a + B4b + B5b + C1 + C2**

Не делать без отдельного OK: агрессивный CSP (B1b), полноценный rate limit (B5a), streaming upload (B4a) — больше объём / риск регрессий.

---

## 6. AI-процесс аудита

- Промпт: Senior security specialist; deps + OWASP + AI review; сначала отчёт → gate → фиксы
- Инструменты: `npm audit`, `pip-audit`, grep/read auth/routes/FE, Issue [#39](https://github.com/Sintik1/Qa_Asistant/issues/39)
- Safety CLI — пропущен (требует interactive login)

---

## 7. Remediations applied (2026-10-05)

| Package | Action |
|---------|--------|
| A2 | `flask-cors>=6`; dotenv/click/anyio/pytest fixed on Python ≥3.10 (CI 3.11); markers for 3.9 residual |
| B1a | Headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` |
| B2a | `LOG_ANALYZE_ADMIN_TOKEN` required when not `TESTING` |
| B3a | Settings: no secret in localStorage; purge legacy key; Home uses `apiReady` only |
| B4b / B5b | skipped as agreed |
| C1 | CI: `npm audit --audit-level=high`, `pip-audit` |
| C2 | README § Security |

Verify: pytest **101** (excl ui/security), vitest **78**, build OK.

---

## 8. Следующий шаг

Шаг 2 закрывается после OK пользователя → далее **шаг 3 OAuth2**.
