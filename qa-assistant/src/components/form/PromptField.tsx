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
        className="w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
      />
      <p className="text-xs text-slate-500">{value.length} символов в промте</p>
    </div>
  )
}
