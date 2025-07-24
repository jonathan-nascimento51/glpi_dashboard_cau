'use client'

import { useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from './useApiQuery'
import type { MetricsOverview } from '../types/metricsOverview'

export const POLLING_INTERVAL_MS = 60000

interface ApiMetricsEntry {
  open_tickets: number
  tickets_closed_this_month: number
}

export function useMetricsOverview() {
  const queryClient = useQueryClient()
  const query = useApiQuery<Record<string, ApiMetricsEntry>, Error>(
    ['metrics-overview'],
    '/metrics/overview',
    {
      refetchInterval: POLLING_INTERVAL_MS,
    },
  )

  const metrics = useMemo(() => {
    if (!query.data) return undefined
    const transformed: MetricsOverview = {}
    for (const level of Object.keys(query.data)) {
      const item = query.data[level]
      transformed[level] = {
        open: item.open_tickets ?? 0,
        closed: item.tickets_closed_this_month ?? 0,
      }
    }
    return transformed
  }, [query.data])

  const refreshMetrics = () =>
    queryClient.invalidateQueries({ queryKey: ['metrics-overview'] })

  return {
    metrics,
    refreshMetrics,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
  }
}
