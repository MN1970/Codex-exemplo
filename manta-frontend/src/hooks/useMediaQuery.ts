import { useSyncExternalStore } from 'react'

function subscribe(query: string, callback: () => void) {
  const mql = window.matchMedia(query)
  mql.addEventListener('change', callback)
  return () => mql.removeEventListener('change', callback)
}

/** Example reusable hook. Add new hooks here as `use<Name>.ts`. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (callback) => subscribe(query, callback),
    () => window.matchMedia(query).matches,
    () => false,
  )
}
