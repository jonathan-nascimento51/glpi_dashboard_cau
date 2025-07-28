import { useMemo } from 'react'
import { useApiQuery } from './useApiQuery'
import type { LevelData } from '../components/LevelsPanel'

interface ApiLevelMetrics {
  new?: number
  pending?: number
  progress?: number
  solved?: number
  resolved?: number
  closed?: number
}

export function useMetricsLevels() {
  const query = useApiQuery<Record<string, ApiLevelMetrics>>(
    ['metrics-levels'],
    '/metrics/levels',
    { refetchInterval: 60000 },
  )

  const levels = useMemo<LevelData[] | undefined>(() => {
    if (!query.data) return undefined
    return Object.entries(query.data)
      .sort(([a], [b]) => {
        const na = parseInt(a.replace(/\D+/g, ''), 10)
        const nb = parseInt(b.replace(/\D+/g, ''), 10)
        return na - nb
      })
      .map(([name, metrics]) => ({
        name,
        metrics: {
          new: metrics.new ?? 0,
          progress: metrics.progress ?? 0,
          pending: metrics.pending ?? 0,
          resolved:
            metrics.resolved ?? metrics.solved ?? metrics.closed ?? 0,
        },
      }))
  }, [query.data])

  return {
    levels,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error as Error | null,
    refresh: () => query.refetch(),
  }
}
