import React, { createContext, useContext, useState, useEffect } from 'react'

type ThemeMode = 'dark' | 'light'

interface ThemeContextType {
  theme: ThemeMode
  toggleTheme: () => void
  setTheme: (theme: ThemeMode) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    // Check localStorage first, then system preference
    const stored = localStorage.getItem('hub-theme')
    if (stored === 'light' || stored === 'dark') {
      return stored
    }

    // Check system preference
    if (
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-color-scheme: light)').matches
    ) {
      return 'light'
    }

    return 'dark'
  })

  useEffect(() => {
    // Update document class and localStorage
    const root = document.documentElement
    root.setAttribute('data-theme', theme)
    localStorage.setItem('hub-theme', theme)

    // Also update color-scheme CSS property
    root.style.colorScheme = theme
  }, [theme])

  const toggleTheme = () => {
    setThemeState(prev => (prev === 'dark' ? 'light' : 'dark'))
  }

  const setTheme = (newTheme: ThemeMode) => {
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
