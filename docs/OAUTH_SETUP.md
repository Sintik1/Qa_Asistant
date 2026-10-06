# OAuth2 setup — QA Assistant (CI/CD ДЗ шаг 3)

Issue: [#40](https://github.com/Sintik1/Qa_Asistant/issues/40)

Секреты провайдеров хранятся **только** в корневом `.env` (gitignored) и/или в **Supabase Dashboard → Auth → Providers**. Никогда в `VITE_*` (кроме publishable anon), никогда в git, Issues или чат.

## Архитектура

| Провайдер | Flow |
|-----------|------|
| **Google** | FE → `supabase.auth.signInWithOAuth({ provider: 'google' })` → Google → Supabase `/auth/v1/callback` → FE `/auth/callback` (PKCE, `detectSessionInUrl`) |
| **Yandex** | FE → `GET /api/auth/oauth/yandex/start` → Yandex → Flask callback → Supabase Admin session → `/auth/callback#tokens` |

Общий endpoint профиля API: `GET /api/auth/me` (Bearer JWT).

> Google **не** требует Flask и `GOOGLE_*` в серверном `.env` для основного UI-пути.  
> Legacy Flask Google (`/api/auth/oauth/google/*`) оставлен опционально, если `GOOGLE_*` заданы.

## 1. Google → Supabase Auth Provider

### 1.1. Google Cloud Console

1. https://console.cloud.google.com/apis/credentials  
2. OAuth client → **Web application**  
3. **Authorized redirect URIs** (обязательно, без trailing slash):

   ```
   https://revyywfeeqdmlgrbakpj.supabase.co/auth/v1/callback
   ```

4. (Опционально) Authorized JavaScript origins:
   - `http://127.0.0.1:5173`
   - `https://sintik1.github.io`
5. Скопируй Client ID / Client Secret (не в чат).

### 1.2. Supabase Dashboard

1. https://supabase.com/dashboard/project/revyywfeeqdmlgrbakpj/auth/providers  
2. **Google** → Enable → вставь Client ID / Secret → Save.  
3. **URL Configuration**  
   https://supabase.com/dashboard/project/revyywfeeqdmlgrbakpj/auth/url-configuration  

   | Поле | Значение |
   |------|----------|
   | Site URL | `http://127.0.0.1:5173` (локально) или `https://sintik1.github.io/Qa_Asistant/` |
   | Redirect URLs | `http://127.0.0.1:5173/auth/callback` |
   | | `http://localhost:5173/auth/callback` |
   | | `https://sintik1.github.io/Qa_Asistant/auth/callback` |

## 2. Yandex OAuth (Flask)

1. https://oauth.yandex.ru/client/new  
2. Callback URI: `http://127.0.0.1:5001/api/auth/oauth/yandex/callback`  
3. Права: `login:email`, `login:info`  
4. ID / пароль → только `.env` (`YANDEX_*`) через `scripts/save_oauth_secrets.py`

Также в `.env`:

```bash
SUPABASE_URL=https://revyywfeeqdmlgrbakpj.supabase.co
SUPABASE_ANON_KEY=...                 # publishable / anon (можно в VITE_*)
SUPABASE_SERVICE_ROLE_KEY=...         # server-only (для Yandex /me session)
OAUTH_API_PUBLIC_URL=http://127.0.0.1:5001
OAUTH_PUBLIC_APP_URL=http://127.0.0.1:5173
```

FE `.env.local`:

```bash
VITE_SUPABASE_URL=https://revyywfeeqdmlgrbakpj.supabase.co
VITE_SUPABASE_ANON_KEY=...
VITE_API_BASE_URL=http://127.0.0.1:5001   # нужен только для Yandex
```

## 3. Проверка

```bash
# Google не зависит от Flask
# UI: http://127.0.0.1:5173/auth → Google → после входа session в Supabase

curl -s http://127.0.0.1:5001/api/auth/oauth/status | jq
# google.flow == "supabase_auth_provider"
# google.supabase_callback == ".../auth/v1/callback"
```

Автотесты:

```bash
pytest tests/test_oauth.py -q
cd qa-assistant && npm test -- AuthPage.test.tsx
```

### 3.1. Troubleshooting: Google

| Симптом | Что проверить |
|---------|----------------|
| `redirect_uri_mismatch` | В Google Console URI = **именно** `https://revyywfeeqdmlgrbakpj.supabase.co/auth/v1/callback` (не Flask `/api/auth/oauth/google/callback`) |
| `redirect_to` not allowed | Supabase → URL Configuration → Redirect URLs включает текущий FE callback |
| Provider disabled | Dashboard → Auth → Providers → Google Enabled |
| Pages deploy | Redirect URL с base path: `https://sintik1.github.io/Qa_Asistant/auth/callback` |

Yandex: callback должен совпадать с `…/api/auth/oauth/yandex/callback` в кабинете oauth.yandex.ru.

## Безопасность

| Правило | Как соблюдено |
|---------|----------------|
| Google Client Secret | только Supabase Dashboard (или legacy `.env`), не в FE |
| Yandex Secret | только server `.env` |
| Secret не в git | `.env` gitignored; в репо только placeholders в `.env.example` |
| Secret не в чат/Issues | вставлять через Dashboard / `save_oauth_secrets.py` |
| State / PKCE | Supabase PKCE (Google); one-time `state` (Yandex Flask) |
| Tokens в URL (Yandex) | fragment `#`, не query |
