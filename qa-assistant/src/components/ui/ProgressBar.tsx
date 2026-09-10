interface ProgressBarProps {
  label: string
  /** 0–100; omit for indeterminate */
  value?: number
}

export function ProgressBar({ label, value }: ProgressBarProps) {
  const indeterminate = value === undefined

  return (
    <div className="w-full" aria-live="polite">
      <p className="mb-2 text-sm text-slate-700">{label}</p>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full bg-violet-600 ${
            indeterminate ? 'w-1/3 animate-pulse' : ''
          }`}
          style={indeterminate ? undefined : { width: `${Math.min(100, Math.max(0, value))}%` }}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={indeterminate ? undefined : value}
          aria-label={label}
        />
      </div>
    </div>
  )
}
