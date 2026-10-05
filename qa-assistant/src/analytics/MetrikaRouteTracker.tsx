import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { initMetrika, trackPageView } from './metrika'

/**
 * Initializes Metrika once and sends SPA hit on every route change.
 * Must render inside <BrowserRouter>.
 */
export function MetrikaRouteTracker() {
  const location = useLocation()

  useEffect(() => {
    initMetrika()
  }, [])

  useEffect(() => {
    trackPageView(`${location.pathname}${location.search}`)
  }, [location.pathname, location.search])

  return null
}
