import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useFilters } from './useFilters'

export function useHotkeys() {
  const { toggleFilters } = useFilters()
  const queryClient = useQueryClient()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!e.ctrlKey) return
      const target = e.target as HTMLElement | null
      const tag = target?.tagName
if (target?.isContentEditable || tag === 'INPUT' || tag === 'TEXTAREA') return
      if (e.key.toLowerCase() === 'r') {
        e.preventDefault()
        queryClient.invalidateQueries()
      } else if (e.key.toLowerCase() === 'f') {
        e.preventDefault()
        toggleFilters()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleFilters, queryClient])
}
