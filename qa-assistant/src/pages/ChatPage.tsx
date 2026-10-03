import { FormEvent, useState } from 'react'
import { chatRequirements, type ChatCitation } from '../api/chat'
import { messageForApiError, resolveApiError } from '../api/errors'
import { PageHeader } from '../components/ui/PageHeader'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'

type ChatTurn = {
  role: 'user' | 'assistant'
  text: string
  citations?: ChatCitation[]
}

export function ChatPage() {
  const [question, setQuestion] = useState('')
  const [documentId, setDocumentId] = useState('')
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (q.length < 2 || busy) return
    setBusy(true)
    setError(null)
    setTurns((prev) => [...prev, { role: 'user', text: q }])
    setQuestion('')
    try {
      const res = await chatRequirements({
        question: q,
        document_id: documentId.trim() || undefined,
      })
      setTurns((prev) => [
        ...prev,
        { role: 'assistant', text: res.answer, citations: res.citations },
      ])
    } catch (err) {
      const resolved = resolveApiError(err)
      setError(messageForApiError(resolved))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6">
      <PageHeader
        title="Чат по требованиям"
        description="RAG по проиндексированным разделам загруженных документов (Supabase + pgvector)."
      />

      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <label className="flex flex-col gap-1 text-sm text-slate-700">
          Document ID (опционально — сузить поиск)
          <input
            className="rounded-md border border-slate-300 px-3 py-2"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="uuid документа"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm text-slate-700">
          Вопрос
          <textarea
            className="min-h-[6rem] rounded-md border border-slate-300 px-3 py-2"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Например: какие условия рассрочки для Wi-Fi роутера?"
          />
        </label>
        <Button type="submit" disabled={busy || question.trim().length < 2}>
          {busy ? 'Думаю…' : 'Спросить'}
        </Button>
      </form>

      {error ? <ErrorMessage message={error} /> : null}

      <div className="flex flex-col gap-4">
        {turns.map((turn, idx) => (
          <article
            key={`${turn.role}-${idx}`}
            className={
              turn.role === 'user'
                ? 'rounded-lg bg-slate-100 px-4 py-3 text-sm'
                : 'rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm'
            }
          >
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
              {turn.role === 'user' ? 'Вы' : 'Ассистент'}
            </div>
            <p className="whitespace-pre-wrap text-slate-800">{turn.text}</p>
            {turn.citations && turn.citations.length > 0 ? (
              <ul className="mt-3 space-y-2 border-t border-slate-100 pt-3 text-xs text-slate-600">
                {turn.citations.map((c, i) => (
                  <li key={`${c.document_id}-${i}`}>
                    <span className="font-medium">
                      {c.section_path || c.title || c.document_id}
                    </span>
                    {typeof c.similarity === 'number'
                      ? ` · sim=${c.similarity.toFixed(3)}`
                      : ''}
                    {c.preview ? (
                      <div className="mt-0.5 text-slate-500">{c.preview}</div>
                    ) : null}
                  </li>
                ))}
              </ul>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  )
}
