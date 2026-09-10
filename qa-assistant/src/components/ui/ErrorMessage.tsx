interface ErrorMessageProps {
  message: string
  actionLabel?: string
  onAction?: () => void
}

export function ErrorMessage({
  message,
  actionLabel,
  onAction,
}: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <p>{message}</p>
      {actionLabel && onAction ? (
        <button
          type="button"
          onClick={onAction}
          className="mt-2 font-semibold text-red-900 underline"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  )
}
