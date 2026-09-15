/** Breakpoints адаптивной вёрстки (mobile-first). Согласованы с `index.css` @media. */

export type BreakpointName = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

export interface BreakpointRange {
  /** Имя точки перелома */
  name: BreakpointName
  /** Минимальная ширина viewport в px (включительно) */
  minWidth: number
  /** Человекочитаемое описание диапазона устройств */
  label: string
}

export type BreakpointMap = Record<BreakpointName, number>
