import { useCallback } from 'react'
import { useTheme } from '../context/theme'

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()

  const handleSetTheme = (theme: string) => setTheme(theme)

  return (
    <div className="theme-switcher">
      <button className={`theme-btn ${theme === 'light' ? 'active' : ''}`} onClick={() => handleSetTheme('light')}>
        Light
      </button>
      <button className={`theme-btn ${theme === 'dark' ? 'active' : ''}`} onClick={() => handleSetTheme('dark')}>
        Dark
      </button>
      <button className={`theme-btn ${theme === 'corporate' ? 'active' : ''}`} onClick={() => handleSetTheme('corporate')}>
        Corp
      </button>
      <button className={`theme-btn ${theme === 'tech' ? 'active' : ''}`} onClick={() => handleSetTheme('tech')}>
        Tech
      </button>
    </div>
  )
}
