import { useMemo } from 'react'
import { useApiQuery } from './useApiQuery'

export interface LevelMetrics {
  new: number
  progress: number
  pending: number
  resolved: number
}

export interface LevelEntry {
  name: string
  metrics: LevelMetrics
}

const LEVELS_QUERY_KEY = ['levels-metrics'] as const

export function useLevelsMetrics() {
  const query = useApiQuery<Record<string, LevelMetrics>>(LEVELS_QUERY_KEY, '/metrics/levels')

  const levels = useMemo<LevelEntry[]>(() => {
    if (!query.data) return []
    return Object.entries(query.data).map(([name, metrics]) => ({ name, metrics }))
  }, [query.data])

  return {
    levels,
    isLoading: query.isLoading,
    isError: query.isError,
  }
}
