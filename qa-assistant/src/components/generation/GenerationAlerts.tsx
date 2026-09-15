import { ErrorMessage } from '../ui/ErrorMessage'
import { ERROR_MESSAGES } from '../../utils/constants'

interface GenerationAlertsProps {
  formError: string | null
  generationError: string | null
  warning: string | null
  onOpenSettings: () => void
  onClearGenerationError: () => void
  onClearRequirements: () => void
  onRetry: () => void
  onClearWarning: () => void
}

/**
 * Stack of form / generation / truncation alerts under the main form.
 */
export function GenerationAlerts({
  formError,
  generationError,
  warning,
  onOpenSettings,
  onClearGenerationError,
  onClearRequirements,
  onRetry,
  onClearWarning,
}: GenerationAlertsProps) {
  return (
    <>
      {formError === ERROR_MESSAGES.MISSING_TOKEN ? (
        <ErrorMessage
          message={formError}
          actionLabel="Настроить токен"
          onAction={onOpenSettings}
        />
      ) : formError ? (
        <ErrorMessage message={formError} />
      ) : null}

      {generationError ? (
        <ErrorMessage
          message={generationError}
          actionLabel={
            generationError === ERROR_MESSAGES.NO_REQUIREMENTS
              ? 'Загрузить другой файл'
              : 'Повторить'
          }
          onAction={() => {
            if (generationError === ERROR_MESSAGES.NO_REQUIREMENTS) {
              onClearRequirements()
              onClearGenerationError()
              return
            }
            onRetry()
          }}
        />
      ) : null}

      {warning ? (
        <ErrorMessage
          message={warning}
          actionLabel="Скрыть"
          onAction={onClearWarning}
        />
      ) : null}
    </>
  )
}
