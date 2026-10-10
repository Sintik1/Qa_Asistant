# Hybrid B — публичный FE/API + локальный AI (Ollama)

Схема: **GitHub Pages (FE)** → **публичный туннель к Flask на Mac** → **Ollama на том же Mac** (`127.0.0.1:11434`).

Проверяющий открывает UI в интернете; генерация работает, пока ноутбук онлайн и туннель жив.

## Компоненты

| Слой | Где | Примечание |
|------|-----|------------|
| Frontend | GitHub Pages `https://sintik1.github.io/Qa_Asistant/` | `VITE_API_BASE_URL` = публичный URL Flask |
| Flask API | этот Mac `:5001` | CORS включает `https://sintik1.github.io` |
| AI | Ollama на `:11434` | Flask ходит на `localhost` — отдельный AI-туннель не нужен |
| Публикация API | Serveo / Pinggy / Cloudflare Tunnel / Render | см. ниже |

Альтернатива «API в облаке»: `Dockerfile.api` + `render.yaml` — Flask на Render, а Ollama тогда нужен **отдельный** публичный URL (туннель с Mac).

## Быстрый старт (этот Mac)

```bash
# 1) Ollama (вне Cursor sandbox; при SIGTRAP — без HTTP_PROXY + OLLAMA_LLM_LIBRARY=cpu)
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
  OLLAMA_HOST=127.0.0.1:11434 OLLAMA_LLM_LIBRARY=cpu \
  ~/.local/ollama-v0.6.5/ollama serve

# 2) Flask
set -a && source .env && set +a
python3 -m flask --app wsgi run -p 5001 --host 127.0.0.1

# 3) Публичный туннель к Flask (Serveo — работает при Clash fake-IP DNS)
ssh -o ServerAliveInterval=30 -R 80:127.0.0.1:5001 serveo.net
# → скопировать https://….serveousercontent.com
```

Хелпер: `./scripts/hybrid_b_start.sh` (Ollama + туннель; `--with-api-tunnel` если нужен второй URL).

## Env

**Локальный `.env` (Flask):**

```env
AI_PROVIDER=ollama
QA_ASISTANT_API_URL=http://localhost:11434/v1/chat/completions
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://sintik1.github.io
OAUTH_PUBLIC_APP_URL=https://sintik1.github.io/Qa_Asistant
OAUTH_API_PUBLIC_URL=https://<api-tunnel-host>
```

**GitHub Actions Variable (Pages build):**

- `VITE_API_BASE_URL` = `https://<api-tunnel-host>` (без trailing slash)

После смены URL — пересобрать Pages (`workflow_dispatch` / push в `main`).

**Supabase Auth → Redirect URLs** (если логин с Pages):

- `https://sintik1.github.io/Qa_Asistant/**`
- Site URL можно оставить локальным для разработки; для прод-логина с Pages — Site URL = Pages app URL.

## Известные ограничения

1. **Quick tunnel URL меняется** при каждом перезапуске Serveo/cloudflared → нужно обновить `VITE_API_BASE_URL` и передеплоить FE (или использовать named tunnel / Render).
2. **Clash / VPN fake-IP (`198.18.0.2`)** ломает Cloudflare quick tunnels (`argotunnel.com` → `240.x`). Обход: Serveo/Pinggy/`bore`, либо отключить fake-IP для `*.argotunnel.com`.
3. Ollama в sandbox Cursor часто падает на Metal discover (`SIGTRAP`) — запускать с `required_permissions/all` или вручную в обычном Terminal.
4. Пока Mac спит / туннель упал — публичный UI не достучится до API.

## Render (опционально, стабильный API URL)

1. Dashboard → Blueprint → `render.yaml`.
2. Secrets: Supabase keys, `CORS_ORIGINS=https://sintik1.github.io`, `QA_ASISTANT_API_URL=https://<ollama-tunnel>/v1/chat/completions`.
3. На Mac: туннель **только** к Ollama; `VITE_API_BASE_URL` = `https://qa-assistant-api.onrender.com`.

## Проверка

```bash
curl -sL "$VITE_API_BASE_URL/api/health"
# из браузера на Pages: Network → /api/health → 200, без CORS error
```
