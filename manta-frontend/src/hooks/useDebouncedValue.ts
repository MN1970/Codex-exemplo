import { useEffect, useState } from 'react'

/**
 * Returns `value`, updated at most once every `delayMs` of quiet time —
 * the standard debounce pattern for search-as-you-type inputs. The
 * component re-renders on every keystroke (fast, uncontrolled feel) but
 * consumers (e.g. the effect that fires the API call) only see the
 * settled value.
 */
export function useDebouncedValue<T>(value: T, delayMs = 350): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])

  return debounced
}
