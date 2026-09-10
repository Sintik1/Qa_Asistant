import type { Config } from 'tailwindcss'

/**
 * Tailwind CSS v4 primarily uses CSS-first config (`@theme` in index.css).
 * This file is kept for tooling compatibility and future theme extensions.
 */
const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}

export default config
