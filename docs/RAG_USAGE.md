# Руководство по RAG (QA Assistant)

Документ для ежедневной работы с RAG: индексация требований, шаблоны/кейсы, просмотр и очистка в Supabase.

Связанная стадия: [#36](https://github.com/Sintik1/Qa_Asistant/issues/36) · миграция: `supabase/migrations/20261003213000_rag_chunks_pgvector.sql`

---

## 1. Что такое RAG в этом проекте

**RAG** = поиск похожих фрагментов в Postgres (pgvector) → подмешивание в промпт ИИ.

| Режим | Когда | Таблица поиска |
|--------|--------|----------------|
| Style / few-shot | при **Generate** | `case_chunks` (шаблоны + **явно** проиндексированные кейсы) |
| Multi-doc | при **Generate** | `document_chunks` **других** документов пользователя |
| Chat | UI **/chat** или `POST /api/chat` | `document_chunks` |

Важно:

- Сырые файлы лежат в **Storage** (`documents` bucket / локальный `uploads/`).
- Для поиска нужны строки в **`document_chunks`** / **`case_chunks`** с заполненным `embedding`.
- После **Generate** кейсы **не** попадают в RAG автоматически (чтобы кривой ответ ИИ не портил базу примеров). Только ручной index или шаблоны.

---

## 2. Подготовка окружения

### 2.1. Переменные `.env` (корень репо)

```bash
# Рекомендуемо для локальной семантики
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMS=768
# EMBEDDING_API_URL=http://localhost:11434/api/embeddings

# Альтернативы:
# EMBEDDING_PROVIDER=hash          # только тесты / offline, смысл поиска слабый
# EMBEDDING_PROVIDER=openai_compat
# EMBEDDING_API_URL=https://api.openai.com/v1/embeddings
# EMBEDDING_API_TOKEN=...
```

### 2.2. Модель эмбеддингов (Ollama)

```bash
ollama pull nomic-embed-text
ollama list   # убедиться, что модель есть
```

### 2.3. Проверка, что RAG включён

```bash
curl -s http://127.0.0.1:5001/api/health | jq .rag
```

Ожидаемо:

```json
{
  "enabled": true,
  "embedding_provider": "ollama",
  "embedding_model": "nomic-embed-text",
  "embedding_dims": 768
}
```

### 2.4. JWT для API

Все `/api/rag/*` и `/api/chat` требуют авторизации (Bearer JWT Supabase), кроме публичного `/api/health`.

Как взять токен:

1. Войти в UI (`/auth`).
2. DevTools → Network → любой запрос к Flask → заголовок `Authorization: Bearer …`.
3. Или Session в Application / логика `supabase.auth.getSession()`.

Дальше в примерах: `export TOKEN='eyJ...'`.

Базовый URL API (локально часто порт **5001**):

```bash
export API=http://127.0.0.1:5001
```

---

## 3. Как добавлять документы в RAG

### 3.1. Обычный путь (рекомендуется) — через UI / upload

1. Открыть Home → загрузить PDF / DOCX / MD.
2. Сервер:
   - сохраняет файл в Storage;
   - парсит разделы (Word Heading и/или нумерация `3` / `3.1`);
   - для каждого leaf-раздела пишет строку в **`document_chunks`** + считает `embedding`.

После upload документ уже в RAG-корпусе для chat и multi-doc.

### 3.2. Через API upload

```bash
curl -s -X POST "$API/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/Trebovania.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  | jq '{id: .document.id, status: .document.status, chars: .char_count}'
```

Запомните `document.id` — пригодится для chat с фильтром.

### 3.3. Повторная индексация текста при Generate

Если кейсы генерируют с `requirements_text` без повторного upload, сервер **переиндексирует** текст документа в `document_chunks` в начале generate (чтобы индекс не отставал).  
Это про **разделы требований**, не про `test_cases`.

### 3.4. Отладка парсинга разделов (до/после индекса)

```bash
python tools/debug_section_parse.py /path/to/file.docx --prompts
python tools/debug_section_parse.py /path/to/file.docx --exclude 1,2 --exclude-title приложение
```

Смотрите `leaf_count`, `section_path`, наличие ли таблицы в `body`.

---

## 4. Как добавлять тест-кейсы в RAG (`case_chunks`)

Есть **только явные** способы. Автопосле Generate — **выключен**.

### 4.1. Шаблоны (эталоны pos / neg / boundary / anti)

Используйте для «идеальных» примеров стиля, не обязательно из текущего прогона.

```bash
curl -s -X POST "$API/api/rag/templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "Позитив: роутер в рассрочку 24 мес",
        "step": "Выбрать Wi-Fi роутер\nВыбрать рассрочку 24 месяца\nОформить заказ",
        "expected_result": "Заказ создан, рассрочка активна",
        "status": "Approved",
        "tags": ["positive"],
        "source_type": "template"
      },
      {
        "name": "Негатив: превышен лимит рассрочки",
        "step": "Смоделировать долг выше лимита\nПопытаться оформить рассрочку",
        "expected_result": "Покупка в рассрочку запрещена",
        "tags": ["negative", "boundary"],
        "source_type": "template"
      },
      {
        "name": "Anti: слишком общий кейс",
        "step": "Проверить систему",
        "expected_result": "Всё работает",
        "tags": ["anti"],
        "source_type": "anti_example"
      }
    ]
  }' | jq
```

Ответ: `{"indexed": N}`.

| Поле | Описание |
|------|----------|
| `name` | Название кейса |
| `step` | Шаги (`\n` = несколько шагов) |
| `expected_result` | Ожидаемый результат |
| `source_type` | `template` \| `anti_example` \| `approved_case` |
| `tags` | массив строк или строка через запятую |
| `status` | обычно `Approved` |

### 4.2. Проверенные кейсы из прогона (после ревью)

1. Generate на Home → получите таблицу кейсов.
2. Исправьте плохие через UI (PATCH) или удалите прогон и перегенерируйте.
3. Только хорошие отправьте в RAG:

**Выбранные id:**

```bash
curl -s -X POST "$API/api/rag/index-cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_ids": [
      "11111111-1111-4111-8111-111111111111",
      "22222222-2222-4222-8222-222222222222"
    ]
  }' | jq
```

**Весь run** (только если вы реально проверили все строки):

```bash
curl -s -X POST "$API/api/rag/index-cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"run_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}' | jq
```

Ответ: `{"indexed": N, "source_type": "approved_case"}`.

Id кейсов: ответ generate → `items[].id`, или Table Editor → `test_cases`.

### 4.3. Чего не делать

- Не полагаться на то, что Generate сам наполнит `case_chunks`.
- Не индексировать весь run, пока не просмотрели шаги/ожидания.
- Не класть секреты/ПДн в шаблоны.

---

## 5. Как пользоваться результатом

### 5.1. Generate (style + multi-doc)

Обычная генерация на Home. Сервер для каждого раздела:

1. ищет похожие записи в `case_chunks`;
2. ищет related куски в `document_chunks` других документов;
3. добавляет их в промпт;
4. генерирует кейсы по **текущему** разделу (пункты → шаги).

Чем качественнее шаблоны/проиндексированные кейсы и чем больше загруженных ТЗ — тем полезнее контекст.

### 5.2. Chat по требованиям

UI: вкладка **«Чат по требованиям»** → `/chat`.

Или API:

```bash
curl -s -X POST "$API/api/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "В какой системе заказ по акции недоступен?",
    "document_id": "опциональный-uuid-документа"
  }' | jq
```

В ответе: `answer` + `citations` (path раздела, preview, similarity).

---

## 6. Просмотр и правка в Supabase (Table Editor)

Dashboard проекта → **Table Editor**.  
Фильтруйте по своему `user_id` (Authentication → Users → User UID).

### 6.1. Таблицы RAG

#### `document_chunks`

| Колонка | Смысл |
|---------|--------|
| `id` | id чанка |
| `user_id` | владелец |
| `document_id` | связь с `documents` |
| `chunk_index` | порядок leaf-секции |
| `section_number` | `4.1`, `3.2.1`, … |
| `section_path` | путь для цитат / промпта |
| `title` | заголовок раздела |
| `content` | текст раздела (+ таблицы pipe-строками) |
| `metadata` | jsonb (флаги вроде has_table) |
| `embedding` | vector(768) — **не редактировать руками** |
| `created_at` / `updated_at` | метки времени |

**Смотреть:** фильтр `document_id` = нужный файл; читайте `section_path` + `content`.  
**Править текст:** можно поправить `content` / `title` / `section_path` в Editor, но **embedding устареет**. После ручной правки текста лучше **перезалить документ** (upload заново) или снова прогнать generate с полным текстом, чтобы пересчитать векторы.

#### `case_chunks`

| Колонка | Смысл |
|---------|--------|
| `id` | id записи RAG |
| `user_id` | владелец |
| `source_type` | `template` / `approved_case` / `anti_example` |
| `test_case_id` | связь с `test_cases` (если индексировали из прогона) |
| `name`, `status`, `step`, `expected_result` | поля кейса |
| `tags` | массив тегов |
| `content` | текст, по которому строился embedding |
| `embedding` | vector(768) |
| `metadata` | jsonb |

**Смотреть:** фильтр `source_type = template` или `approved_case`.  
**Править:** можно изменить `name`/`step`/`expected_result`/`tags`, но снова нужен пересчёт embedding через API (`/rag/templates` или `/rag/index-cases`), иначе поиск будет по старому вектору. Практичнее: удалить строку и заново проиндексировать правильный кейс.

### 6.2. Связанные таблицы (не RAG, но рядом)

| Таблица | Роль |
|--------|------|
| `documents` | мета файла, `storage_path` |
| `generation_runs` | прогоны generate |
| `test_cases` | кейсы прогона (источник для ручного index) |
| `generation_chunks` | **не** корпус RAG (debug AI по чанкам прогона) |

Storage: **Storage** → bucket `documents` — исходные файлы.

### 6.3. SQL Editor (удобные запросы)

Список разделов документа:

```sql
select chunk_index, section_number, section_path, left(content, 120) as preview
from document_chunks
where user_id = 'ВАШ_USER_UUID'
  and document_id = 'ВАШ_DOCUMENT_UUID'
order by chunk_index;
```

Шаблоны и approved для RAG:

```sql
select source_type, name, tags, left(content, 100) as preview, created_at
from case_chunks
where user_id = 'ВАШ_USER_UUID'
order by created_at desc;
```

Проверка, что embedding не null:

```sql
select
  (select count(*) from document_chunks where user_id = 'ВАШ_USER_UUID' and embedding is null) as docs_without_emb,
  (select count(*) from case_chunks where user_id = 'ВАШ_USER_UUID' and embedding is null) as cases_without_emb;
```

---

## 7. Как чистить RAG

RLS: обычный пользователь через PostgREST видит только свои строки. В Dashboard (service role) можно чистить шире — будьте осторожны.

### 7.1. Удалить чанки одного документа

Table Editor → `document_chunks` → Filter `document_id` → Delete rows.

Или SQL:

```sql
delete from document_chunks
where user_id = 'ВАШ_USER_UUID'
  and document_id = 'ВАШ_DOCUMENT_UUID';
```

Файл в Storage и строка в `documents` останутся — при желании удалите их отдельно. После повторного upload индекс создастся снова.

### 7.2. Удалить все document_chunks пользователя

```sql
delete from document_chunks where user_id = 'ВАШ_USER_UUID';
```

### 7.3. Удалить шаблоны / approved кейсы из RAG

Один тип:

```sql
delete from case_chunks
where user_id = 'ВАШ_USER_UUID'
  and source_type = 'template';
```

Конкретные id:

```sql
delete from case_chunks
where user_id = 'ВАШ_USER_UUID'
  and id in ('uuid-1', 'uuid-2');
```

Всё по пользователю:

```sql
delete from case_chunks where user_id = 'ВАШ_USER_UUID';
```

Удаление из `case_chunks` **не** удаляет строки из `test_cases` (рабочая таблица прогона).

### 7.4. Полный «сброс знаний» пользователя (требования + кейсы RAG)

```sql
delete from case_chunks where user_id = 'ВАШ_USER_UUID';
delete from document_chunks where user_id = 'ВАШ_USER_UUID';
```

Прогоны/файлы при этом могут остаться — чистите `test_cases` / `generation_runs` / `documents` / Storage отдельно, если нужен полный wipe продукта.

---

## 8. Типовой рабочий день (чеклист)

1. `ollama pull nomic-embed-text` (если ещё нет) + Flask/Vite запущены.  
2. Загрузить ТЗ (DOCX/MD) → проверить в Table Editor рост `document_chunks`.  
3. При необходимости залить эталоны: `POST /api/rag/templates`.  
4. Generate → **вручную** проверить кейсы.  
5. Хорошие кейсы: `POST /api/rag/index-cases` с `case_ids`.  
6. Chat `/chat` для вопросов по ТЗ.  
7. Мусор / устаревшее: удалить строки в `document_chunks` / `case_chunks` (см. §7).

---

## 9. Частые проблемы

| Симптом | Что проверить |
|---------|----------------|
| Chat: «ничего не найдено» | Был ли upload? Есть ли строки в `document_chunks`? Тот же `user_id`? |
| Style не влияет на generate | Есть ли `case_chunks`? Не пустой ли `embedding`? |
| Поиск «глупый» | `EMBEDDING_PROVIDER=hash` или нет модели Ollama |
| Размеры вектора | `EMBEDDING_DIMS` должен быть **768** (как в миграции) |
| Правили `content` в Editor | Нужна переиндексация (upload / templates / index-cases) |
| Путаница с `generation_chunks` | Это debug прогона, не корпус RAG |

---

## 10. Сводка API

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/api/documents/upload` | файл → extract → **index document_chunks** |
| `POST` | `/api/runs/<id>/generate` | generate (+ RAG enrich); **без** auto case index |
| `POST` | `/api/rag/templates` | добавить эталоны в `case_chunks` |
| `POST` | `/api/rag/index-cases` | добавить **проверенные** кейсы в `case_chunks` |
| `POST` | `/api/chat` | Q&A по `document_chunks` |
| `GET` | `/api/health` | блок `.rag` |

Отладка парсера без API: `tools/debug_section_parse.py`.

---

_Последнее обновление: 2026-10-03 · Issue [#36](https://github.com/Sintik1/Qa_Asistant/issues/36)._
