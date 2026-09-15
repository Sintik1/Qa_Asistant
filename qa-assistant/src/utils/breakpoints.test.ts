import { describe, expect, it } from 'vitest'
import {
  BREAKPOINTS,
  maxWidthQuery,
  minWidthQuery,
} from './breakpoints'

describe('breakpoints', () => {
  it('exposes mobile-first widths matching index.css media queries', () => {
    expect(BREAKPOINTS).toEqual({
      xs: 0,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
    })
  })

  it('builds min/max media query strings', () => {
    expect(minWidthQuery(768)).toBe('(min-width: 768px)')
    expect(maxWidthQuery(768)).toBe('(max-width: 767px)')
  })
})
