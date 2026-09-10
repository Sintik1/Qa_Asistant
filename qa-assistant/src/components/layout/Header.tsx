import { APP_SUBTITLE, APP_TITLE } from '../../utils/constants'

export function Header() {
  return (
    <header className="bg-gradient-to-r from-violet-600 to-orange-500 px-4 py-6 text-center text-white">
      <h1 className="text-2xl font-bold md:text-3xl">{APP_TITLE}</h1>
      <p className="mt-1 text-sm opacity-95 md:text-base">{APP_SUBTITLE}</p>
    </header>
  )
}
