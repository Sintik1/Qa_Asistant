import { SELECT_CLASS } from '../../utils/formStyles'

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
        className={SELECT_CLASS}
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
