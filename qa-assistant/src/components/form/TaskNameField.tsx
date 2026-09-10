interface TaskNameFieldProps {
  value: string
  onChange: (value: string) => void
}

export function TaskNameField({ value, onChange }: TaskNameFieldProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="task-name" className="block text-sm font-medium text-slate-800">
        Название задачи
      </label>
      <input
        id="task-name"
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Например: CRM-1234 Map"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
      />
      <p className="text-xs text-slate-500">
        Если не заполнено — используется имя файла требований. Имя скачиваемого
        CSV: «Тест кейсы_{'<название>'}.csv».
      </p>
    </div>
  )
}
