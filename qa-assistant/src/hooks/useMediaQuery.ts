import { useCallback, useSyncExternalStore } from 'react'

/**
 * Подписка на CSS media query (например `(min-width: 768px)`).
 * SSR-safe: на сервере / без `matchMedia` возвращает `defaultMatches`.
 */
export function useMediaQuery(
  query: string,
  defaultMatches = false,
): boolean {
  const subscribe = useCallback(
    (onStoreChange: () => void) => {
      if (
        typeof window === 'undefined' ||
        typeof window.matchMedia !== 'function'
      ) {
        return () => {}
      }

      const media = window.matchMedia(query)
      media.addEventListener('change', onStoreChange)
      return () => media.removeEventListener('change', onStoreChange)
    },
    [query],
  )

  const getSnapshot = useCallback(() => {
    if (
      typeof window === 'undefined' ||
      typeof window.matchMedia !== 'function'
    ) {
      return defaultMatches
    }
    return window.matchMedia(query).matches
  }, [query, defaultMatches])

  const getServerSnapshot = useCallback(
    () => defaultMatches,
    [defaultMatches],
  )

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}
