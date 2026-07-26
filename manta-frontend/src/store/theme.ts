import { create } from 'zustand'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'manta-theme'

function getSystemTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') return stored
  return getSystemTheme()
}

function applyTheme(theme: Theme) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('dark', theme === 'dark')
  document.documentElement.setAttribute('data-theme', theme)
}

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

/**
 * Global theme store (zustand). Call `useThemeStore.getState().setTheme(...)`
 * outside components, or `useThemeStore((s) => s.theme)` inside them.
 * Applied on load by `initTheme()`, invoked once from main.tsx.
 */
export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: getInitialTheme(),
  setTheme: (theme) => {
    window.localStorage.setItem(STORAGE_KEY, theme)
    applyTheme(theme)
    set({ theme })
  },
  toggleTheme: () => {
    const next: Theme = get().theme === 'dark' ? 'light' : 'dark'
    get().setTheme(next)
  },
}))

/** Apply the persisted/system theme to <html> before first paint. */
export function initTheme() {
  applyTheme(useThemeStore.getState().theme)
}
