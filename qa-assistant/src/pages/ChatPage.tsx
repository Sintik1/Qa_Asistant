import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useRagChat } from '../hooks/useRagChat'
import type { ChatCitation } from '../api/chat'
import { MarkdownAnswer } from '../components/chat/MarkdownAnswer'
import { PageHeader } from '../components/ui/PageHeader'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { SELECT_CLASS, TEXTAREA_CLASS } from '../utils/formStyles'

function citationLabel(c: ChatCitation): string {
  const title = c.section_path || c.title || c.document_id
  if (c.url) return `Страница: ${title}`
  const kind = c.source_kind === 'case' ? 'Кейс' : 'Требование'
  return `${kind}: ${title}`
}

export function ChatPage() {
  const chat = useRagChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const node = bottomRef.current
    if (node && typeof node.scrollIntoView === 'function') {
      node.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [chat.turns, chat.busy])

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-0 py-2 sm:gap-6">
      <PageHeader
        title="Чат по проекту"
        description="Задайте вопрос — в ответ попадают страницы с близким сходством, как они записаны в пространстве."
      />

      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
        <span
          className={`rounded-full px-2.5 py-1 font-medium ${
            chat.ragEnabled
              ? 'bg-emerald-50 text-emerald-800'
              : chat.ragEnabled === false
                ? 'bg-amber-50 text-amber-800'
                : 'bg-slate-100 text-slate-600'
          }`}
        >
          RAG:{' '}
          {chat.ragEnabled
            ? 'включён'
            : chat.ragEnabled === false
              ? 'выключен'
              : 'статус неизвестен'}
        </span>
        {chat.ragHint ? <span>{chat.ragHint}</span> : null}
      </div>

      <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3 sm:p-4">
        <label className="flex flex-col gap-1 text-sm text-slate-700" htmlFor="chat-document">
          Документ (опционально — сузить поиск)
          <select
            id="chat-document"
            className={SELECT_CLASS}
            value={chat.documentId}
            onChange={(e) => chat.setDocumentId(e.target.value)}
          >
            <option value="">Все загруженные документы</option>
            {chat.documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.original_filename}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            className="size-4 accent-violet-700"
            checked={chat.includeCases}
            onChange={(e) => chat.setIncludeCases(e.target.checked)}
          />
          Искать также в шаблонах и проиндексированных кейсах
        </label>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="secondary"
            className="!w-auto"
            disabled={chat.busy}
            onClick={() => void chat.onSyncConfluence()}
          >
            Синхронизировать Confluence
          </Button>
          {chat.syncNote ? <span className="text-sm text-slate-600">{chat.syncNote}</span> : null}
        </div>
        {chat.documents.length === 0 ? (
          <p className="text-sm text-slate-600">
            Индекс пуст, пока нет загруженных файлов.{' '}
            <Link to="/" className="font-medium text-violet-700 underline">
              Загрузить требования
            </Link>
          </p>
        ) : null}
      </div>

      <div
        className="flex min-h-[16rem] flex-col gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4"
        aria-live="polite"
      >
        {chat.turns.length === 0 && !chat.busy ? (
          <p className="m-auto max-w-md text-center text-sm text-slate-500">
            Пример: «Как подключить услугу Домофон?» — в ответ попадает текст
            найденной страницы, без пересказа.
          </p>
        ) : null}
        {chat.turns.map((turn, idx) => (
          <article
            key={`${turn.role}-${idx}`}
            className={
              turn.role === 'user'
                ? 'ml-6 rounded-lg bg-violet-50 px-4 py-3 text-sm sm:ml-12'
                : 'mr-6 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm sm:mr-12'
            }
          >
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
              {turn.role === 'user' ? 'Вы' : 'Ассистент'}
            </div>
            {turn.role === 'assistant' ? (
              <MarkdownAnswer text={turn.text} />
            ) : (
              <p className="whitespace-pre-wrap text-slate-800">{turn.text}</p>
            )}
            {turn.citations && turn.citations.length > 0 ? (
              <ul className="mt-3 space-y-2 border-t border-slate-100 pt-3 text-xs text-slate-600">
                {turn.citations.map((c, i) => (
                  <li key={`${c.document_id}-${i}`}>
                    <span className="font-medium">{citationLabel(c)}</span>
                    {typeof c.similarity === 'number'
                      ? ` · сходство ${c.similarity.toFixed(3)}`
                      : ''}
                    {c.preview && !c.url ? (
                      <div className="mt-0.5 text-slate-500">{c.preview}</div>
                    ) : null}
                    {c.url ? (
                      <div className="mt-0.5">
                        <a
                          href={c.url}
                          className="text-violet-700 underline"
                          target="_blank"
                          rel="noreferrer"
                        >
                          Открыть в Confluence
                        </a>
                      </div>
                    ) : null}
                  </li>
                ))}
              </ul>
            ) : null}
          </article>
        ))}
        {chat.busy ? (
          <p className="text-sm text-slate-500" role="status">
            Ищу в базе и формирую ответ…
          </p>
        ) : null}
        <div ref={bottomRef} />
      </div>

      {chat.error ? <ErrorMessage message={chat.error} /> : null}

      <form onSubmit={chat.onSubmit} className="flex flex-col gap-3">
        <label className="flex flex-col gap-1 text-sm text-slate-700" htmlFor="chat-question">
          Вопрос
          <textarea
            id="chat-question"
            className={`${TEXTAREA_CLASS} min-h-[6rem]`}
            value={chat.question}
            onChange={(e) => chat.setQuestion(e.target.value)}
            placeholder="Например: какие условия рассрочки для Wi-Fi роутера?"
            disabled={chat.busy}
          />
        </label>
        <Button type="submit" disabled={chat.busy || chat.question.trim().length < 2}>
          {chat.busy ? 'Думаю…' : 'Спросить'}
        </Button>
      </form>
    </div>
  )
}
