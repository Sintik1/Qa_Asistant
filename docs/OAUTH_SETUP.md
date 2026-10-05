# OAuth2 setup — QA Assistant (CI/CD ДЗ шаг 3)

Issue: [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)

Секреты хранятся **только** в корневом `.env` (gitignored). Никогда в `VITE_*`, никогда в git.

## Архитектура

| Провайдер | Flow |
|-----------|------|
| **Google** | FE → `GET /api/auth/oauth/google/start` → Google → Flask callback → Supabase Admin session → `/auth/callback#tokens` |
| **Yandex** | FE → `GET /api/auth/oauth/yandex/start` → Yandex → Flask callback → Supabase Admin session → `/auth/callback#tokens` |

Общий endpoint профиля: `GET /api/auth/me` (Bearer JWT).

> Оба провайдера идут через **Flask** (не требуют включения Google в Supabase Dashboard Providers). Нужен `SUPABASE_SERVICE_ROLE_KEY` (или новый `sb_secret_…`) для создания сессии.

## 1. Google Cloud Console

1. https://console.cloud.google.com/apis/credentials  
2. OAuth client → **Web application**  
3. Authorized redirect URIs (обязательно):
   - `http://127.0.0.1:5001/api/auth/oauth/google/callback`
4. (Опционально origins) `http://127.0.0.1:5173`  
5. Client ID / Secret → `.env` (`GOOGLE_*`) или:

```bash
python3 scripts/save_oauth_secrets.py
```

## 2. Yandex OAuth

1. https://oauth.yandex.ru/client/new  
2. Callback URI: `http://127.0.0.1:5001/api/auth/oauth/yandex/callback`  
3. Права: `login:email`, `login:info`  
4. ID / пароль → `.env` (`YANDEX_*`)

## 3. Supabase (только service key)

В `.env`:

```bash
SUPABASE_URL=https://revyywfeeqdmlgrbakpj.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...   # legacy JWT service_role ИЛИ sb_secret_…
OAUTH_API_PUBLIC_URL=http://127.0.0.1:5001
OAUTH_PUBLIC_APP_URL=http://127.0.0.1:5173
```

## 4. Проверка

```bash
curl -s http://127.0.0.1:5001/api/auth/oauth/status | jq
# UI: http://127.0.0.1:5173/auth → Google / Yandex
# После входа: GET /api/auth/me с Bearer JWT
```

Автотесты:

```bash
pytest tests/test_oauth.py -q
cd qa-assistant && npm test -- AuthPage.test.tsx
```

## Безопасность

| Правило | Как соблюдено |
|---------|----------------|
| Secret не в FE | только server `.env` |
| Secret не в git | `.env` gitignored |
| State CSRF | one-time `state` per provider |
| Tokens в URL | fragment `#`, не query |
