import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark' | 'corporate' | 'tech'

export function useThemeSwitcher() {
  const [theme, setTheme] = useState<Theme>('dark')

  useEffect(() => {
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved) setTheme(saved)
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  return { theme, setTheme }
}
