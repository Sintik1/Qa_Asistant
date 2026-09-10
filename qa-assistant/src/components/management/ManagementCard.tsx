import { Button } from '../ui/Button'

interface ManagementCardProps {
  title: string
  addLabel: string
  refreshLabel?: string
  onAdd?: () => void
  onRefresh?: () => void
}

export function ManagementCard({
  title,
  addLabel,
  refreshLabel = 'Обновить список',
  onAdd,
  onRefresh,
}: ManagementCardProps) {
  return (
    <section className="rounded-md border border-violet-300 p-4">
      <div className="mb-3 h-0.5 w-full bg-orange-400" aria-hidden />
      <h2 className="mb-3 text-base font-semibold text-slate-900">{title}</h2>
      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={onAdd} className="w-auto">
          {addLabel}
        </Button>
        <Button variant="success" onClick={onRefresh} className="w-auto">
          {refreshLabel}
        </Button>
      </div>
    </section>
  )
}
