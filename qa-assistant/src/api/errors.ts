import { ERROR_MESSAGES } from '../utils/constants'

export class ApiRequestError extends Error {
  readonly code: string
  readonly status: number
  readonly requestId?: string

  constructor(
    code: string,
    message: string,
    status: number,
    requestId?: string,
  ) {
    super(message)
    this.name = 'ApiRequestError'
    this.code = code
    this.status = status
    this.requestId = requestId
  }
}

export type ApiErrorAction = {
  message: string
  /** Soft navigation hint for callers (auth / settings). */
  redirectTo?: '/auth' | '/settings'
  requestId?: string
}

export function resolveApiError(error: unknown): ApiErrorAction {
  if (error instanceof ApiRequestError) {
    const known = ERROR_MESSAGES[error.code as keyof typeof ERROR_MESSAGES]
    const message = known ?? error.message
    if (
      error.status === 401 ||
      error.code === 'UNAUTHORIZED' ||
      error.code === 'INVALID_TOKEN'
    ) {
      return {
        message,
        redirectTo: error.code === 'INVALID_TOKEN' ? '/settings' : '/auth',
        requestId: error.requestId,
      }
    }
    if (error.status === 403 || error.code === 'FORBIDDEN') {
      return { message, redirectTo: '/auth', requestId: error.requestId }
    }
    if (error.code === 'MISSING_TOKEN') {
      return { message, redirectTo: '/settings', requestId: error.requestId }
    }
    return { message, requestId: error.requestId }
  }
  if (error instanceof TypeError) {
    return { message: ERROR_MESSAGES.API_UNAVAILABLE }
  }
  if (error instanceof Error && error.message) {
    return { message: error.message }
  }
  return { message: ERROR_MESSAGES.API_UNAVAILABLE }
}

export function messageForApiError(error: unknown): string {
  return resolveApiError(error).message
}

export async function parseApiError(response: Response): Promise<ApiRequestError> {
  let code = 'INTERNAL_ERROR'
  let message =
    ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES] ??
    'Внутренняя ошибка сервера. Повторите попытку позже.'
  let requestId = response.headers.get('X-Request-Id') ?? undefined

  // Network-ish HTTP statuses without JSON still map to TZ strings.
  if (response.status === 401) code = 'UNAUTHORIZED'
  else if (response.status === 403) code = 'FORBIDDEN'
  else if (response.status === 500) code = 'INTERNAL_ERROR'

  try {
    const body = (await response.json()) as {
      error?: { code?: string; message?: string; request_id?: string }
    }
    if (body.error?.code) code = body.error.code
    if (body.error?.message) message = body.error.message
    else {
      const known = ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES]
      if (known) message = known
    }
    if (body.error?.request_id) requestId = body.error.request_id
  } catch {
    const known = ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES]
    if (known) message = known
  }

  return new ApiRequestError(code, message, response.status, requestId)
}
