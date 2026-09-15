import type { ChunkMethod, ChunkSettings } from '../../types'

interface ChunkSettingsFormProps {
  value: ChunkSettings
  onChange: (next: ChunkSettings) => void
  disabled?: boolean
}

const METHODS: { value: ChunkMethod; label: string }[] = [
  { value: 'header', label: 'По заголовкам (header)' },
  { value: 'fixed', label: 'Фиксированная длина (fixed)' },
  { value: 'recursive', label: 'Адаптивный (recursive)' },
]

/** SHOULD HAVE S1: размер чанка / перекрытие / метод перед перегенерацией. */
export function ChunkSettingsForm({
  value,
  onChange,
  disabled = false,
}: ChunkSettingsFormProps) {
  return (
    <fieldset
      disabled={disabled}
      className="space-y-3 rounded-md border border-slate-200 bg-slate-50 p-4"
    >
      <legend className="px-1 text-sm font-semibold text-slate-800">
        Параметры чанкинга
      </legend>

      <div className="grid gap-3 sm:grid-cols-3">
        <label className="block text-sm text-slate-700">
          Размер чанка
          <input
            type="number"
            min={500}
            max={20000}
            step={100}
            value={value.chunkSize}
            onChange={(e) =>
              onChange({ ...value, chunkSize: Number(e.target.value) || 0 })
            }
            className="mt-1 min-h-11 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
          />
        </label>

        <label className="block text-sm text-slate-700">
          Перекрытие
          <input
            type="number"
            min={0}
            max={5000}
            step={50}
            value={value.chunkOverlap}
            onChange={(e) =>
              onChange({
                ...value,
                chunkOverlap: Number(e.target.value) || 0,
              })
            }
            className="mt-1 min-h-11 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
          />
        </label>

        <label className="block text-sm text-slate-700">
          Метод
          <select
            value={value.chunkMethod}
            onChange={(e) =>
              onChange({
                ...value,
                chunkMethod: e.target.value as ChunkMethod,
              })
            }
            className="mt-1 min-h-11 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
          >
            {METHODS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </label>
      </div>
    </fieldset>
  )
}
