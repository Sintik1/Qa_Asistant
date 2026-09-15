import { APP_SUBTITLE, APP_TITLE } from '../../utils/constants'

export function Header() {
  return (
    <header className="app-shell__header app-gradient text-center text-white">
      <h1 className="app-shell__header-title font-bold">{APP_TITLE}</h1>
      <p className="app-shell__header-subtitle mt-1 opacity-95">{APP_SUBTITLE}</p>
    </header>
  )
}
