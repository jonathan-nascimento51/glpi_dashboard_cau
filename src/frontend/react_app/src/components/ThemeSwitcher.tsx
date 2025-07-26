import { useCallback } from 'react'
import { useTheme } from '../context/theme'

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()

  const setLight = useCallback(() => setTheme('light'), [setTheme])
  const setDark = useCallback(() => setTheme('dark'), [setTheme])
  const setCorporate = useCallback(() => setTheme('corporate'), [setTheme])
  const setTech = useCallback(() => setTheme('tech'), [setTheme])

  return (
    <div className="theme-switcher">
      <button className={`theme-btn ${theme === 'light' ? 'active' : ''}`} onClick={setLight}>
        Light
      </button>
      <button className={`theme-btn ${theme === 'dark' ? 'active' : ''}`} onClick={setDark}>
        Dark
      </button>
      <button className={`theme-btn ${theme === 'corporate' ? 'active' : ''}`} onClick={setCorporate}>
        Corp
      </button>
      <button className={`theme-btn ${theme === 'tech' ? 'active' : ''}`} onClick={setTech}>
        Tech
      </button>
    </div>
  )
}
