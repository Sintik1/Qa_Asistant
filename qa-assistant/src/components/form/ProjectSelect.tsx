interface ProjectSelectProps {
  value: string
  options: string[]
  onChange: (value: string) => void
}

export function ProjectSelect({ value, options, onChange }: ProjectSelectProps) {
  return (
    <div className="space-y-2">
      <label
        htmlFor="project-id"
        className="block text-sm font-medium text-slate-800"
      >
        ID проекта (для контекста и обучения)
      </label>
      <select
        id="project-id"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  )
}
