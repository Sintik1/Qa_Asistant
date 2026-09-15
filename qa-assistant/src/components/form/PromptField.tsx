import { TEXTAREA_CLASS } from '../../utils/formStyles'

interface PromptFieldProps {
  value: string
  onChange: (value: string) => void
}

export function PromptField({ value, onChange }: PromptFieldProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="prompt" className="block text-sm font-medium text-slate-800">
        Промт для нейросети
      </label>
      <textarea
        id="prompt"
        rows={6}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Введите промт для генерации тест-кейсов..."
        className={TEXTAREA_CLASS}
      />
      <p className="text-xs text-slate-500">{value.length} символов в промте</p>
    </div>
  )
}
