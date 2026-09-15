/** Shared Tailwind for text inputs / selects (touch target ≥44px). */
export const INPUT_CLASS =
  'min-h-11 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200'

export const SELECT_CLASS = `${INPUT_CLASS} bg-white`

/** Textarea: same chrome, no fixed min-height (rows control size). */
export const TEXTAREA_CLASS =
  'w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200'
