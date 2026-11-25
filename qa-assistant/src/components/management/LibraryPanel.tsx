import { useCallback, useEffect, useState } from 'react'
import {
  createLibraryItem,
  deleteLibraryItem,
  listLibrary,
  type LibraryItem,
  type LibraryKind,
} from '../../api/library'
import { ApiRequestError } from '../../api/errors'
import { resolveApiError } from '../../api/errors'
import { Button } from '../ui/Button'
import { INPUT_CLASS, TEXTAREA_CLASS } from '../../utils/formStyles'
import { ManagementCard } from './ManagementCard'

interface LibraryPanelProps {
  title: string
  addLabel: string
  kind: LibraryKind
  selectedId?: string | null
  onUse: (item: LibraryItem) => void
  onClearSelection?: () => void
  onDeleted?: (id: string) => void
}

export function LibraryPanel({
  title,
  addLabel,
  kind,
  selectedId,
  onUse,
  onClearSelection,
  onDeleted,
}: LibraryPanelProps) {
  const [items, setItems] = useState<LibraryItem[]>([])
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [content, setContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    setError(null)
    try {
      setItems(await listLibrary(kind))
    } catch (err) {
      setError(messageOf(err))
    }
  }, [kind])

  useEffect(() => {
    void load()
  }, [load])

  const save = async () => {
    setBusy(true)
    setError(null)
    try {
      await createLibraryItem(kind, { name, content })
      setName('')
      setContent('')
      setOpen(false)
      await load()
    } catch (err) {
      setError(messageOf(err))
    } finally {
      setBusy(false)
    }
  }

  const remove = async (id: string) => {
    setError(null)
    try {
      await deleteLibraryItem(kind, id)
      onDeleted?.(id)
      await load()
    } catch (err) {
      setError(messageOf(err))
    }
  }

  return (
    <section className="space-y-3">
      <ManagementCard
        title={title}
        addLabel={addLabel}
        onAdd={() => {
          setOpen((value) => !value)
          setError(null)
        }}
        onRefresh={() => {
          void load()
        }}
      />
      {open ? (
        <div className="space-y-2 rounded-md border border-slate-200 p-3">
          <label className="block text-sm font-medium text-slate-800" htmlFor={`${kind}-name`}>
            Имя
          </label>
          <input
            id={`${kind}-name`}
            value={name}
            onChange={(event) => setName(event.target.value)}
            className={INPUT_CLASS}
            maxLength={200}
          />
          <label className="block text-sm font-medium text-slate-800" htmlFor={`${kind}-content`}>
            Текст
          </label>
          <textarea
            id={`${kind}-content`}
            rows={5}
            value={content}
            onChange={(event) => setContent(event.target.value)}
            className={TEXTAREA_CLASS}
          />
          <Button type="button" variant="secondary" disabled={busy} onClick={() => void save()}>
            Сохранить
          </Button>
        </div>
      ) : null}
      {error ? (
        <p className="text-sm text-red-700" role="alert">
          {error}
        </p>
      ) : null}
      {items.length === 0 ? (
        <p className="text-xs text-slate-500">Список пуст</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => {
            const selected = item.id === selectedId
            return (
              <li
                key={item.id}
                className="flex flex-col gap-2 rounded-md border border-slate-200 p-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900">{item.name}</p>
                  <p className="text-xs text-slate-500">{item.content.length} символов</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button type="button" variant="secondary" onClick={() => onUse(item)}>
                    Использовать
                  </Button>
                  {selected && onClearSelection ? (
                    <Button type="button" variant="secondary" onClick={onClearSelection}>
                      Снять выбор
                    </Button>
                  ) : null}
                  <Button type="button" variant="success" onClick={() => void remove(item.id)}>
                    Удалить
                  </Button>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}

function messageOf(error: unknown): string {
  if (error instanceof ApiRequestError && error.message) {
    return error.message
  }
  return resolveApiError(error).message
}
