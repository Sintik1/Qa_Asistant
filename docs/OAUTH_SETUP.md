# OAuth2 setup — QA Assistant (CI/CD ДЗ шаг 3)

Issue: [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)

Секреты хранятся **только** в корневом `.env` (gitignored). Никогда в `VITE_*`, никогда в git.

## Архитектура

| Провайдер | Flow |
|-----------|------|
| **Google** | Frontend `supabase.auth.signInWithOAuth({ provider: 'google' })` → Supabase Auth → JWT |
| **Yandex** | Frontend → `GET /api/auth/oauth/yandex/start` → Yandex → Flask callback → Supabase Admin session → `/auth/callback#tokens` |

Общий endpoint профиля: `GET /api/auth/me` (Bearer JWT).

## 1. Google Cloud Console

1. https://console.cloud.google.com/apis/credentials  
2. Create OAuth client ID → **Web application**  
3. Authorized JavaScript origins:
   - `http://127.0.0.1:5173`
   - `http://localhost:5173`
   - `https://revyywfeeqdmlgrbakpj.supabase.co`
4. Authorized redirect URIs:
   - `https://revyywfeeqdmlgrbakpj.supabase.co/auth/v1/callback`
5. Скопируйте **Client ID** и **Client Secret**.

Сохранить локально:

```bash
python3 scripts/save_oauth_secrets.py
# или вручную в .env: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
```

В **Supabase Dashboard** → Authentication → Providers → **Google** → Enable → вставить те же Client ID/Secret → Save.

Redirect URLs (Authentication → URL Configuration):

- Site URL: `http://127.0.0.1:5173`
- Redirect URLs: `http://127.0.0.1:5173/auth/callback`, `http://localhost:5173/auth/callback`

## 2. Yandex OAuth

1. https://oauth.yandex.ru/client/new  
2. Платформы: **Веб-сервисы**  
3. Callback URI: `http://127.0.0.1:5001/api/auth/oauth/yandex/callback`  
4. Права: `login:email`, `login:info`  
5. Скопируйте ID и пароль приложения → `scripts/save_oauth_secrets.py` (`YANDEX_*`).

Также в `.env` (server):

```bash
SUPABASE_SERVICE_ROLE_KEY=...   # Dashboard → Settings → API (secret!)
OAUTH_API_PUBLIC_URL=http://127.0.0.1:5001
OAUTH_PUBLIC_APP_URL=http://127.0.0.1:5173
```

## 3. Проверка

```bash
# статус провайдеров (без секретов)
curl -s http://127.0.0.1:5001/api/auth/oauth/status | jq

# UI
# http://127.0.0.1:5173/auth → «Войти через Google» / «Войти через Yandex»
# После входа: GET /api/auth/me с Bearer JWT → user_id + email
```

Автотесты (моки, без реальных консолей):

```bash
pytest tests/test_oauth.py -q
cd qa-assistant && npm test -- AuthPage.test.tsx
```

## Безопасность

| Правило | Как соблюдено |
|---------|----------------|
| Secret не в FE | только server `.env` / Supabase Dashboard |
| Secret не в git | `.env` gitignored; в репо — `.env.example` placeholders |
| State CSRF (Yandex) | one-time `state` в памяти процесса |
| Tokens в URL | Yandex отдаёт tokens в **hash** (`#`), не в query |
