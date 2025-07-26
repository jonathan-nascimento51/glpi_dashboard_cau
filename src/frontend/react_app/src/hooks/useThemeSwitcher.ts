export { type Theme } from '../context/theme'
import { useTheme } from '../context/theme'

export function useThemeSwitcher() {
  return useTheme()
}
