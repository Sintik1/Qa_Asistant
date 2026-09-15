import { BREAKPOINTS, minWidthQuery } from '../utils/breakpoints'
import { useMediaQuery } from './useMediaQuery'
import type { BreakpointName } from '../types/breakpoints'

export interface BreakpointFlags {
  /** ≥ 640px */
  isSmUp: boolean
  /** ≥ 768px */
  isMdUp: boolean
  /** ≥ 1024px */
  isLgUp: boolean
  /** ≥ 1280px */
  isXlUp: boolean
  /** Текущий ближайший breakpoint (mobile-first) */
  current: BreakpointName
}

/**
 * Флаги breakpoints для условного UI (карточки вместо таблицы и т.п.).
 */
export function useBreakpoint(): BreakpointFlags {
  const isSmUp = useMediaQuery(minWidthQuery(BREAKPOINTS.sm))
  const isMdUp = useMediaQuery(minWidthQuery(BREAKPOINTS.md))
  const isLgUp = useMediaQuery(minWidthQuery(BREAKPOINTS.lg))
  const isXlUp = useMediaQuery(minWidthQuery(BREAKPOINTS.xl))

  let current: BreakpointName = 'xs'
  if (isXlUp) current = 'xl'
  else if (isLgUp) current = 'lg'
  else if (isMdUp) current = 'md'
  else if (isSmUp) current = 'sm'

  return { isSmUp, isMdUp, isLgUp, isXlUp, current }
}
