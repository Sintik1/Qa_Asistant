# OAuth2 setup — QA Assistant (CI/CD ДЗ шаг 3)

Issue: [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)

Секреты хранятся **только** в корневом `.env` (gitignored). Никогда в `VITE_*`, никогда в git, Issues или чат.

## Архитектура

| Провайдер | Flow |
|-----------|------|
| **Google** | FE → `GET /api/auth/oauth/google/start` → Google → Flask callback → Supabase Admin session → `/auth/callback#tokens` |
| **Yandex** | FE → `GET /api/auth/oauth/yandex/start` → Yandex → Flask callback → Supabase Admin session → `/auth/callback#tokens` |

Общий endpoint профиля: `GET /api/auth/me` (Bearer JWT).

> Оба провайдера идут через **Flask** (не требуют включения Google в Supabase Dashboard Providers). Нужен server-only `SUPABASE_SERVICE_ROLE_KEY` (Dashboard → Settings → API) для создания сессии.

## 1. Google Cloud Console

1. https://console.cloud.google.com/apis/credentials  
2. OAuth client → **Web application**  
3. Authorized redirect URIs (обязательно):
   - `http://127.0.0.1:5001/api/auth/oauth/google/callback`
4. (Опционально origins) `http://127.0.0.1:5173`  
5. Client ID / Secret → только `.env` (`GOOGLE_*`):

```bash
python3 scripts/save_oauth_secrets.py
```

## 2. Yandex OAuth

1. https://oauth.yandex.ru/client/new  
2. Callback URI: `http://127.0.0.1:5001/api/auth/oauth/yandex/callback`  
3. Права: `login:email`, `login:info`  
4. ID / пароль → только `.env` (`YANDEX_*`) через `scripts/save_oauth_secrets.py`

## 3. Supabase (только service key)

В `.env` (не коммитить):

```bash
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=...                 # publishable / anon (можно в VITE_*)
SUPABASE_SERVICE_ROLE_KEY=...         # server-only
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

### 4.1. Troubleshooting: `redirect_uri_mismatch` (Google)

Если Google показывает **Error 400: redirect_uri_mismatch**:

1. Открой [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) → свой OAuth Web client.
2. В **Authorized redirect URIs** добавь **точно** (без trailing slash):
   - `http://127.0.0.1:5001/api/auth/oauth/google/callback`
3. `localhost` ≠ `127.0.0.1` для Google — совпадение должно быть побайтовое с `OAUTH_API_PUBLIC_URL` + path из `/api/auth/oauth/status` → `google.redirect_uri`.
4. Подожди 1–5 минут после сохранения и повтори `/auth` → Google.

Yandex: callback должен совпадать с `…/api/auth/oauth/yandex/callback` в кабинете oauth.yandex.ru.
## Безопасность

| Правило | Как соблюдено |
|---------|----------------|
| Secret не в FE | только server `.env` |
| Secret не в git | `.env` gitignored; в репо только placeholders в `.env.example` |
| Secret не в чат/Issues | вставлять через `save_oauth_secrets.py` или редактор `.env` |
| Утечка в чат | **перевыпустить** ключи в консолях провайдеров |
| State CSRF | one-time `state` per provider |
| Tokens в URL | fragment `#`, не query |
