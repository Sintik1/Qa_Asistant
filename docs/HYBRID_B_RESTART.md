# Hybrid B — подробная инструкция: поднять всё после выключения Mac

Документ для схемы **B**: публичный Frontend (GitHub Pages) + публичный API (туннель к Flask на Mac) + **локальный AI (Ollama на этом же Mac)**.

Связанные файлы: [`HYBRID_LOCAL_AI.md`](HYBRID_LOCAL_AI.md) · [`scripts/hybrid_b_start.sh`](../scripts/hybrid_b_start.sh) · эпик [#37](https://github.com/Sintik1/Qa_Asistant/issues/37).

---

## 0. Как это устроено (чтобы понимать шаги)

```text
Браузер проверяющего
        │
        ▼
https://sintik1.github.io/Qa_Asistant/     ← GitHub Pages (FE, всегда в облаке)
        │
        │  запросы к API (URL зашит при сборке как VITE_API_BASE_URL)
        ▼
https://….serveousercontent.com           ← Serveo-туннель (интернет → твой Mac)
        │
        ▼
Flask на Mac :5001
        │
        ▼
Ollama на Mac :11434                      ← модели лежат локально
```

| Компонент | Где живёт после reboot | Нужно ли поднимать вручную |
|-----------|------------------------|----------------------------|
| GitHub Pages (UI) | Облако GitHub | Нет |
| Supabase (Auth/DB) | Облако | Нет |
| Ollama | Только на Mac | **Да** |
| Flask | Только на Mac | **Да** |
| Serveo-туннель | Только пока открыт SSH | **Да** |
| Связка Pages → API | Variable `VITE_API_BASE_URL` + пересборка Pages | **Да, если URL туннеля новый** |

Важно:

1. После выключения Mac **публичный UI остаётся**, но **generate/API не работают**, пока снова не поднимешь Flask + туннель + (часто) не обновишь URL в Pages.
2. URL Serveo **почти всегда новый** при каждом `ssh … serveo.net`. Старый URL из прошлой сессии мёртв.
3. Не усыпляй Mac и не закрывай 3 терминала, пока нужен доступ из интернета.

---

## 1. Перед стартом (один раз проверить)

### 1.1. Путь к проекту

```bash
cd /Users/vlad/Downloads/ДЗ
```

Дальше все команды — из этого каталога, если не сказано иное.

### 1.2. Что должно уже быть на диске

| Что | Как проверить |
|-----|----------------|
| Python venv | `test -x .venv/bin/python && echo OK` |
| Файл `.env` | `test -f .env && echo OK` (секреты, не в git) |
| Ollama binary | `test -x ~/.local/ollama-v0.6.5/ollama && echo OK` |
| Модель | после старта Ollama: `curl -s http://127.0.0.1:11434/api/tags` — есть `qwen2.5:1.5b` |
| GitHub CLI | `gh auth status` |
| SSH | `ssh -V` |

Если Ollama/модели нет:

```bash
./scripts/setup_ollama.sh 1.5b
```

Если `gh` не залогинен:

```bash
gh auth login
```

### 1.3. В `.env` должны быть (уже настроены ранее)

Минимум для Hybrid B:

```env
AI_PROVIDER=ollama
QA_ASISTANT_API_URL=http://localhost:11434/v1/chat/completions
QA_ASISTANT_API_TOKEN=ollama
QA_ASISTANT_MODEL=qwen2.5:1.5b
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080,https://sintik1.github.io
OAUTH_PUBLIC_APP_URL=https://sintik1.github.io/Qa_Asistant
```

`OAUTH_API_PUBLIC_URL` можно обновить после появления нового Serveo URL (см. шаг 5).

---

## 2. Подъём: три терминала (основной способ)

Открой **Terminal.app** (не обязательно Cursor). Лучше три вкладки/окна.

Не запускай Ollama из песочницы Cursor без полных прав — бывает `SIGTRAP` на Metal. Обычный Terminal надёжнее.

---

### Терминал A — Ollama

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
  OLLAMA_HOST=127.0.0.1:11434 OLLAMA_LLM_LIBRARY=cpu \
  ~/.local/ollama-v0.6.5/ollama serve
```

Окно **не закрывать**. Ожидаемые строки в логе: `Listening on 127.0.0.1:11434`.

Проверка в **четвёртом** маленьком окне или новой вкладке:

```bash
curl -s http://127.0.0.1:11434/api/tags | head -c 300; echo
```

Должен быть JSON со списком моделей (есть `qwen2.5:1.5b`).

Если порт занят старым процессом:

```bash
pkill -f 'ollama serve' || true
# затем снова команда serve выше
```

---

### Терминал B — Flask API

```bash
cd /Users/vlad/Downloads/ДЗ
set -a && source .env && set +a
.venv/bin/python -m flask --app wsgi run -p 5001 --host 127.0.0.1
```

Окно **не закрывать**. Должно быть что-то вроде `Running on http://127.0.0.1:5001`.

Проверка:

```bash
curl -s http://127.0.0.1:5001/api/health | head -c 400; echo
```

В JSON: `"api":"qa-assistant"`, `"ai":{"configured":true,...}`.

Если порт занят:

```bash
lsof -nP -iTCP:5001 -sTCP:LISTEN
# убить PID, затем снова flask
kill <PID>
```

**Не используй** системный `python3` без venv — там часто нет Flask. Нужен именно `.venv/bin/python`.

---

### Терминал C — публичный туннель (Serveo)

Сначала убедись, что Flask уже отвечает на `:5001`, потом:

```bash
ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 \
  -R 80:127.0.0.1:5001 serveo.net
```

Окно **не закрывать**.

В выводе появится строка вида:

```text
Forwarding HTTP traffic from https://XXXXXXXX-YY-YY-YY-YY.serveousercontent.com
```

Скопируй этот `https://…serveousercontent.com` целиком — это **публичный API URL**.  
Дальше в инструкции он обозначается как `$API`.

Проверка с Mac:

```bash
API='https://ВСТАВЬ-СЮДА-URL'
curl -sL -A 'Mozilla/5.0' "$API/api/health" | head -c 400; echo
```

Должен вернуться тот же health JSON, что и с `127.0.0.1:5001`.

Сохрани URL в файл (удобно для следующих команд):

```bash
cd /Users/vlad/Downloads/ДЗ
echo 'https://ВСТАВЬ-СЮДА-URL' > logs/api-tunnel.url
```

---

## 3. Привязать GitHub Pages к новому API URL

Serveo URL после reboot **новый**. Старая сборка Pages всё ещё бьёт в **старый** мёртвый адрес → в браузере «не подключается к API».

### 3.1. Записать Variable

```bash
cd /Users/vlad/Downloads/ДЗ
API=$(tr -d '\r' < logs/api-tunnel.url)
echo "Будет записано: $API"

gh variable set VITE_API_BASE_URL -R Sintik1/Qa_Asistant --body "$API"
gh variable list -R Sintik1/Qa_Asistant | grep VITE_API
```

### 3.2. Пересобрать и задеплоить Pages

```bash
gh workflow run CI -R Sintik1/Qa_Asistant
```

Смотреть статус:

```bash
gh run list -R Sintik1/Qa_Asistant -L 3
# или ждать конкретный run:
gh run watch -R Sintik1/Qa_Asistant
```

Нужны **три зелёных job**: Frontend, Backend, **Deploy frontend (GitHub Pages)**.

Обычно 1–3 минуты.

### 3.3. (Опционально) обновить локальный `.env`

```bash
# подставь актуальный $API
# OAUTH_API_PUBLIC_URL=https://….serveousercontent.com
```

Для generate с Pages это не критично; важно для Yandex OAuth callback через Flask.

Flask после правки `.env` нужно **перезапустить** (Ctrl+C в терминале B → снова команда flask). Туннель C можно не трогать, если Flask снова слушает `:5001`.

---

## 4. Проверка, что всё связано

### 4.1. Локально

```bash
curl -s http://127.0.0.1:11434/api/tags | head -c 100; echo
curl -s http://127.0.0.1:5001/api/health | head -c 200; echo
API=$(tr -d '\r' < /Users/vlad/Downloads/ДЗ/logs/api-tunnel.url)
curl -sL -A 'Mozilla/5.0' "$API/api/health" | head -c 200; echo
```

### 4.2. CORS (Pages → API)

```bash
API=$(tr -d '\r' < /Users/vlad/Downloads/ДЗ/logs/api-tunnel.url)
curl -si -X OPTIONS "$API/api/health" \
  -H 'Origin: https://sintik1.github.io' \
  -H 'Access-Control-Request-Method: GET' | grep -i access-control
```

Ожидается: `Access-Control-Allow-Origin: https://sintik1.github.io`.

### 4.3. Что зашито в Pages

После деплоя открой сайт и в DevTools → Network вызови любое действие, либо:

```bash
# вытащить URL из свежего JS-бандла
HTML=$(curl -sL 'https://sintik1.github.io/Qa_Asistant/')
JS=$(echo "$HTML" | grep -oE 'assets/index-[^"]+\.js' | head -1)
curl -sL "https://sintik1.github.io/Qa_Asistant/$JS" \
  | tr '"' '\n' | grep serveousercontent | head -3
```

Строка должна **совпадать** с текущим `$API` из `logs/api-tunnel.url`.  
Если не совпадает — Variable не обновили или деплой не дождались → повтори шаг 3.

### 4.4. Браузер

1. Открой https://sintik1.github.io/Qa_Asistant/ (лучше hard refresh: Cmd+Shift+R).
2. Войди (Supabase email/password или Google).
3. На Home должен быть режим API «подключён».
4. Загрузи небольшой `.md`/`.docx` и нажми генерацию — ответ идёт через туннель на твой Ollama (может занять минуты на слабом Mac).

---

## 5. Короткий чеклист «после включения»

- [ ] Терминал A: Ollama слушает `:11434`
- [ ] Терминал B: Flask отвечает на `/api/health`
- [ ] Терминал C: Serveo показывает `https://….serveousercontent.com`
- [ ] `curl` на этот URL → health OK
- [ ] `gh variable set VITE_API_BASE_URL …`
- [ ] `gh workflow run CI` → Deploy зелёный
- [ ] В бандле Pages тот же Serveo URL
- [ ] Mac не спит, Clash/VPN не рвёт SSH

---

## 6. Упрощённый вариант (скрипт)

Когда Flask уже запущен (терминал B), можно:

```bash
cd /Users/vlad/Downloads/ДЗ
./scripts/hybrid_b_start.sh
```

Скрипт:

- поднимет Ollama, если лежит;
- поднимет Serveo-туннель к `:5001`;
- напечатает публичный URL и подсказку для `VITE_API_BASE_URL`.

Flask скрипт **сам не стартует** — его нужно запустить отдельно (терминал B).  
Variable + `gh workflow run` всё равно делаешь вручную (шаг 3).

Другие провайдеры туннеля (если Serveo недоступен):

```bash
./scripts/hybrid_b_start.sh --provider pinggy
./scripts/hybrid_b_start.sh --provider bore
# cloudflared часто ломается при Clash fake-IP DNS (198.18.0.2)
./scripts/hybrid_b_start.sh --provider cloudflared
```

---

## 7. Как корректно остановить перед выключением

В каждом терминале:

1. **C (Serveo):** `Ctrl+C` — публичный API сразу недоступен.
2. **B (Flask):** `Ctrl+C`.
3. **A (Ollama):** `Ctrl+C` (или `pkill -f 'ollama serve'`).

Pages и Supabase выключать не нужно.

После следующего включения снова шаги 2 → 3 → 4.

---

## 8. Частые проблемы

| Симптом | Причина | Что сделать |
|---------|---------|-------------|
| Pages открывается, generate падает / «нет API» | Старый `VITE_API_BASE_URL` или туннель мёртв | Шаг 3 + проверь терминал C |
| `curl` на Serveo → 502 | Flask не запущен / упал | Терминал B, снова `/api/health` на localhost |
| Ollama: `could not connect` / SIGTRAP | Прокси или sandbox | Команда из терминала A с `env -u HTTP_PROXY…` и `OLLAMA_LLM_LIBRARY=cpu` |
| `No module named flask` | Запуск не из `.venv` | Только `.venv/bin/python -m flask …` |
| Cloudflare Tunnel 5xx | Clash fake-IP DNS | Используй Serveo/Pinggy, не cloudflared |
| CORS error в браузере | В `CORS_ORIGINS` нет `https://sintik1.github.io` | Добавь в `.env`, перезапусти Flask |
| `gh: not logged in` | Нет auth | `gh auth login` |
| CI Deploy skipped | Старый workflow без `workflow_dispatch` | На `main` уже разрешён deploy на dispatch; смотри job «Deploy frontend» |
| Google login с Pages | Redirect URL в Supabase | Должен быть `https://sintik1.github.io/Qa_Asistant/**` (настраивалось ранее) |

Логи на Mac:

```text
logs/ollama-serve.log
logs/flask-5001.log          # если запускал через nohup
logs/serveo-api.log          # если писали вывод ssh в файл
logs/api-tunnel.url          # последний известный публичный URL
```

---

## 9. Только локальная работа (без интернета / без Pages)

Если не нужен доступ проверяющему из сети — туннель и Variable **не нужны**:

```bash
# A: Ollama (как выше)
# B: Flask (как выше)
cd /Users/vlad/Downloads/ДЗ/qa-assistant
# в qa-assistant/.env.local:
# VITE_API_BASE_URL=http://127.0.0.1:5001
npm run dev
```

Открывай http://127.0.0.1:5173 — это отдельный локальный режим, не GitHub Pages.

---

## 10. Сводная «шпаргалка» (скопировать целиком)

```bash
# === A: Ollama ===
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
  OLLAMA_HOST=127.0.0.1:11434 OLLAMA_LLM_LIBRARY=cpu \
  ~/.local/ollama-v0.6.5/ollama serve

# === B: Flask (другой терминал) ===
cd /Users/vlad/Downloads/ДЗ
set -a && source .env && set +a
.venv/bin/python -m flask --app wsgi run -p 5001 --host 127.0.0.1

# === C: Serveo (третий терминал; Flask уже up) ===
ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 \
  -R 80:127.0.0.1:5001 serveo.net
# скопировать https://….serveousercontent.com

# === Привязка Pages (четвёртый терминал) ===
cd /Users/vlad/Downloads/ДЗ
API='https://ВСТАВЬ-URL-ИЗ-SERVEO'
echo "$API" > logs/api-tunnel.url
curl -sL -A 'Mozilla/5.0' "$API/api/health" | head -c 200; echo
gh variable set VITE_API_BASE_URL -R Sintik1/Qa_Asistant --body "$API"
gh workflow run CI -R Sintik1/Qa_Asistant
gh run watch -R Sintik1/Qa_Asistant

# сайт: https://sintik1.github.io/Qa_Asistant/
```

---

_Последнее обновление: 2026-10-10 — Hybrid B (Pages + Serveo + local Ollama)._
