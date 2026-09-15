import { useEffect, useState } from 'react'

/**
 * Подписка на CSS media query (например `(min-width: 768px)`).
 * SSR-safe: на первом рендере возвращает `defaultMatches`.
 */
export function useMediaQuery(
  query: string,
  defaultMatches = false,
): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return defaultMatches
    }
    return window.matchMedia(query).matches
  })

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return
    }

    const media = window.matchMedia(query)
    const onChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    setMatches(media.matches)
    media.addEventListener('change', onChange)
    return () => media.removeEventListener('change', onChange)
  }, [query])

  return matches
}
