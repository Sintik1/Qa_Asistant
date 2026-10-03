import { ERROR_MESSAGES } from '../utils/constants'

export class ApiRequestError extends Error {
  readonly code: string
  readonly status: number

  constructor(code: string, message: string, status: number) {
    super(message)
    this.name = 'ApiRequestError'
    this.code = code
    this.status = status
  }
}

export function messageForApiError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    const known = ERROR_MESSAGES[error.code as keyof typeof ERROR_MESSAGES]
    return known ?? error.message
  }
  if (error instanceof TypeError) {
    return ERROR_MESSAGES.API_UNAVAILABLE
  }
  if (error instanceof Error && error.message) {
    return error.message
  }
  return ERROR_MESSAGES.API_UNAVAILABLE
}

export async function parseApiError(response: Response): Promise<ApiRequestError> {
  let code = 'INTERNAL_ERROR'
  let message =
    ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES] ??
    'Внутренняя ошибка сервера. Повторите попытку позже.'

  try {
    const body = (await response.json()) as {
      error?: { code?: string; message?: string }
    }
    if (body.error?.code) code = body.error.code
    if (body.error?.message) message = body.error.message
    else {
      const known = ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES]
      if (known) message = known
    }
  } catch {
    /* non-JSON body */
  }

  return new ApiRequestError(code, message, response.status)
}
