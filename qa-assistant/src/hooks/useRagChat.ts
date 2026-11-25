import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { trackGoal } from '../analytics/metrika'
import { chatRequirements, syncConfluenceSpace, type ChatCitation } from '../api/chat'
import { listDocuments } from '../api/documents'
import { messageForApiError, resolveApiError } from '../api/errors'
import { getHealth } from '../api/settings'
import type { ApiDocument } from '../api/types'

export type ChatTurn = {
  role: 'user' | 'assistant'
  text: string
  citations?: ChatCitation[]
}

export function useRagChat() {
  const [question, setQuestion] = useState('')
  const [documentId, setDocumentId] = useState('')
  const [includeCases, setIncludeCases] = useState(true)
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [documents, setDocuments] = useState<ApiDocument[]>([])
  const [ragEnabled, setRagEnabled] = useState<boolean | null>(null)
  const [ragHint, setRagHint] = useState<string | null>(null)
  const [syncNote, setSyncNote] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const [docs, health] = await Promise.all([
          listDocuments().catch(() => [] as ApiDocument[]),
          getHealth().catch(() => null),
        ])
        if (cancelled) return
        setDocuments(docs)
        const enabled = health?.rag?.enabled ?? null
        setRagEnabled(enabled)
        if (health?.rag) {
          const model = health.rag.embedding_model || health.rag.embedding_provider
          setRagHint(model ? `эмбеддинги: ${model}` : null)
        }
      } catch {
        if (!cancelled) setRagEnabled(null)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const onSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault()
      const q = question.trim()
      if (q.length < 2 || busy) return
      setBusy(true)
      setError(null)
      setTurns((prev) => [...prev, { role: 'user', text: q }])
      setQuestion('')
      trackGoal('chat_send')
      try {
        const res = await chatRequirements({
          question: q,
          document_id: documentId.trim() || undefined,
          include_cases: includeCases,
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
    },
    [busy, documentId, includeCases, question],
  )

  const onSyncConfluence = useCallback(async () => {
    if (busy) return
    setBusy(true)
    setError(null)
    setSyncNote(null)
    try {
      const result = await syncConfluenceSpace()
      const docs = await listDocuments().catch(() => [] as ApiDocument[])
      setDocuments(docs)
      setSyncNote(
        `Confluence ${result.space}: проиндексировано ${result.indexed}, без изменений ${result.skipped}`,
      )
    } catch (err) {
      const resolved = resolveApiError(err)
      setError(messageForApiError(resolved))
    } finally {
      setBusy(false)
    }
  }, [busy])

  return {
    question,
    setQuestion,
    documentId,
    setDocumentId,
    includeCases,
    setIncludeCases,
    turns,
    busy,
    error,
    documents,
    ragEnabled,
    ragHint,
    syncNote,
    onSubmit,
    onSyncConfluence,
  }
}
