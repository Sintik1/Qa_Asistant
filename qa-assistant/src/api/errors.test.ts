import { describe, expect, it } from 'vitest'
import { ApiRequestError, messageForApiError, resolveApiError } from './errors'

describe('resolveApiError', () => {
  it('maps 401 to auth redirect', () => {
    const err = new ApiRequestError('UNAUTHORIZED', 'Требуется авторизация.', 401, 'r1')
    expect(resolveApiError(err)).toEqual({
      message: 'Требуется авторизация.',
      redirectTo: '/auth',
      requestId: 'r1',
    })
  })

  it('maps 403 to auth redirect', () => {
    const err = new ApiRequestError('FORBIDDEN', 'Недостаточно прав для выполнения операции.', 403)
    expect(resolveApiError(err).redirectTo).toBe('/auth')
  })

  it('maps network TypeError to API_UNAVAILABLE', () => {
    expect(messageForApiError(new TypeError('Failed to fetch'))).toContain(
      'Не удалось подключиться',
    )
  })

  it('maps INVALID_TOKEN to settings', () => {
    const err = new ApiRequestError('INVALID_TOKEN', 'bad', 401)
    expect(resolveApiError(err).redirectTo).toBe('/settings')
  })
})
