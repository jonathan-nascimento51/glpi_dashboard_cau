'use client'

import { useCallback, useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from './useApiQuery'
import type { MetricsOverview } from '../types/metricsOverview'

export const POLLING_INTERVAL_MS = 60000

const METRICS_QUERY_KEY = ['metrics-overview'] as const

interface ApiMetricsOverview {
  open_tickets: Record<string, number>
  tickets_closed_this_month: Record<string, number>
}

export function useMetricsOverview() {
  const queryClient = useQueryClient()
  const query = useApiQuery<ApiMetricsOverview>(
    METRICS_QUERY_KEY,
    '/metrics/aggregated',
    {
      refetchInterval: POLLING_INTERVAL_MS,
    },
  )

  const metrics = useMemo(() => {
    if (!query.data) return undefined
    const openLevels = Object.keys(query.data.open_tickets);
    const closedLevels = Object.keys(query.data.tickets_closed_this_month);
    const allLevels = Array.from(new Set([...openLevels, ...closedLevels]));
    return allLevels.reduce((acc, level) => {
      acc[level] = {
        open: query.data.open_tickets[level] ?? 0,
        closed: query.data.tickets_closed_this_month[level] ?? 0,
      };
      return acc;
    }, {} as MetricsOverview);
  }, [query.data])

  const refreshMetrics = useCallback(
    () => queryClient.invalidateQueries({ queryKey: METRICS_QUERY_KEY }),
    [queryClient],
  )

  return {
    metrics,
    refreshMetrics,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
  }
}
