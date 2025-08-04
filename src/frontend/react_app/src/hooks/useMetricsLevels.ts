import { useMemo } from 'react'
import { useApiQuery } from './useApiQuery'
import type { LevelData } from '../components/LevelsPanel'

interface ApiLevelMetrics {
  new?: number
  pending?: number
  progress?: number
  resolved?: number
  // Support legacy field names (e.g. "solved" or "closed") via index signature
  [status: string]: number | undefined
}

export function useMetricsLevels() {
  const query = useApiQuery<Record<string, ApiLevelMetrics>>(
    ['metrics-levels'],
    '/v1/metrics/levels',
    { refetchInterval: 60000 },
  )

  const levels = useMemo<LevelData[] | undefined>(() => {
    if (!query.data) return undefined
    return Object.entries(query.data)
      .sort(([a], [b]) => {
        const parseLevelName = (name: string) => {
          return name.match(/(\d+|\D+)/g)?.map(part => isNaN(Number(part)) ? part : Number(part)) || [];
        };
        const componentsA = parseLevelName(a);
        const componentsB = parseLevelName(b);
        for (let i = 0; i < Math.max(componentsA.length, componentsB.length); i++) {
          const partA = componentsA[i];
          const partB = componentsB[i];
          if (partA === undefined) return -1;
          if (partB === undefined) return 1;
          if (typeof partA === 'number' && typeof partB === 'number') {
            if (partA !== partB) return partA - partB;
          } else if (partA !== partB) {
            return partA < partB ? -1 : 1;
          }
        }
        return 0;
      })
      .map(([name, metrics]) => ({
        name,
        metrics: {
          new: metrics.new ?? 0,
          progress: metrics.progress ?? 0,
          pending: metrics.pending ?? 0,
          resolved:
            metrics.resolved ?? metrics['solved'] ?? metrics['closed'] ?? 0,
        },
      }));
  }, [query.data])

  return {
    levels,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error as Error | null,
    refresh: () => query.refetch(),
  }
}
