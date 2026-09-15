import type { BreakpointMap, BreakpointRange } from '../types/breakpoints'

/**
 * Mobile-first breakpoints (px).
 * Должны совпадать с `@media` в `src/index.css` и Tailwind defaults.
 */
export const BREAKPOINTS: BreakpointMap = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
}

export const BREAKPOINT_RANGES: BreakpointRange[] = [
  { name: 'xs', minWidth: BREAKPOINTS.xs, label: 'Phone (portrait)' },
  { name: 'sm', minWidth: BREAKPOINTS.sm, label: 'Phone (landscape) / small tablet' },
  { name: 'md', minWidth: BREAKPOINTS.md, label: 'Tablet' },
  { name: 'lg', minWidth: BREAKPOINTS.lg, label: 'Laptop / desktop' },
  { name: 'xl', minWidth: BREAKPOINTS.xl, label: 'Wide desktop' },
]

/** CSS media query: viewport ≥ minWidth */
export function minWidthQuery(minWidth: number): string {
  return `(min-width: ${minWidth}px)`
}

/** CSS media query: viewport < maxWidth (exclusive upper bound) */
export function maxWidthQuery(maxWidth: number): string {
  return `(max-width: ${maxWidth - 1}px)`
}
