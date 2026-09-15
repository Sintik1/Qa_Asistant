import { Button } from '../ui/Button'

interface ManagementCardProps {
  title: string
  addLabel: string
  refreshLabel?: string
  onAdd?: () => void
  onRefresh?: () => void
  /** Подсказка, когда действия ещё не подключены (mock/backend later). */
  unavailableHint?: string
}

export function ManagementCard({
  title,
  addLabel,
  refreshLabel = 'Обновить список',
  onAdd,
  onRefresh,
  unavailableHint = 'Доступно после подключения бэкенда',
}: ManagementCardProps) {
  const addEnabled = typeof onAdd === 'function'
  const refreshEnabled = typeof onRefresh === 'function'
  const showHint = !addEnabled && !refreshEnabled

  return (
    <section className="rounded-md border border-violet-300 p-4">
      <div className="mb-3 h-0.5 w-full bg-orange-400" aria-hidden />
      <h2 className="mb-3 text-base font-semibold text-slate-900">{title}</h2>
      <div className="flex flex-wrap gap-3">
        <Button
          variant="secondary"
          onClick={onAdd}
          className="w-auto"
          disabled={!addEnabled}
          title={addEnabled ? undefined : unavailableHint}
        >
          {addLabel}
        </Button>
        <Button
          variant="success"
          onClick={onRefresh}
          className="w-auto"
          disabled={!refreshEnabled}
          title={refreshEnabled ? undefined : unavailableHint}
        >
          {refreshLabel}
        </Button>
      </div>
      {showHint ? (
        <p className="mt-2 text-xs text-slate-500">{unavailableHint}</p>
      ) : null}
    </section>
  )
}
