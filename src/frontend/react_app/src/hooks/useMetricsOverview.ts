'use client'

import { useCallback, useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from './useApiQuery'
import type { MetricsOverview } from '../types/metricsOverview'

export const POLLING_INTERVAL_MS = 60000

const METRICS_QUERY_KEY = ['metrics-overview'] as const

interface ApiMetricsEntry {
  open_tickets: number
  tickets_closed_this_month: number
}

export function useMetricsOverview() {
  const queryClient = useQueryClient()
  const query = useApiQuery<Record<string, ApiMetricsEntry>>(
    METRICS_QUERY_KEY,
    '/v1/metrics/overview',
    {
      refetchInterval: POLLING_INTERVAL_MS,
    },
  )

  const metrics = useMemo(() => {
    if (!query.data) return undefined
    return Object.fromEntries(
      Object.entries(query.data).map(([level, item]) => [
        level,
        {
          open: item.open_tickets,
          closed: item.tickets_closed_this_month,
        },
      ]),
    ) as MetricsOverview
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
