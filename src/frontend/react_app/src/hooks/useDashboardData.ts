'use client';

import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from './useApiQuery'
import type { FiltersState } from './useFilters'
import { buildQueryString } from '../lib/buildQueryString'
import { stableStringify } from '../lib/stableStringify'
import type { Chart as ChartType } from 'chart.js'
import type { DashboardStats } from '../types/dashboard'
import { useSparkline } from './useSparkline'
import {
  scheduleIdleCallback,
  cancelIdleCallback,
  type IdleHandle,
} from '../lib/scheduleIdleCallback'

export type Metrics = DashboardStats

interface Aggregated {
  status: Record<string, number>
}

export function useDashboardData(filters?: FiltersState) {
  const queryClient = useQueryClient()
  const qs = buildQueryString(filters)
  const serialized = stableStringify(filters)
  const query = useApiQuery<Aggregated>(
    ['metrics-aggregated', serialized],
    `/metrics/aggregated${qs}`,
    {
      // Automatically refetch metrics every 30 seconds
      refetchInterval: 30000,
    },
  )

  const metrics: Metrics = {
    new: query.data?.status?.new ?? 0,
    pending: query.data?.status?.pending ?? 0,
    progress: query.data?.status?.progress ?? 0,
    resolved: query.data?.status?.resolved ?? 0,
  }
  const [history, setHistory] = useState<Record<keyof Metrics, number[]>>({
    new: [],
    pending: [],
    progress: [],
    resolved: [],
  })
  const trendChart = useRef<ChartType | null>(null)
  const sparkRefs = {
    new: useRef<HTMLCanvasElement>(null),
    pending: useRef<HTMLCanvasElement>(null),
    progress: useRef<HTMLCanvasElement>(null),
    resolved: useRef<HTMLCanvasElement>(null),
  }

  useSparkline(sparkRefs.new, history.new)
  useSparkline(sparkRefs.pending, history.pending)
  useSparkline(sparkRefs.progress, history.progress)
  useSparkline(sparkRefs.resolved, history.resolved)

  useEffect(() => {
    if (!query.data) return
    setHistory((prev) => ({
      new: [...prev.new.slice(-19), metrics.new],
      pending: [...prev.pending.slice(-19), metrics.pending],
      progress: [...prev.progress.slice(-19), metrics.progress],
      resolved: [...prev.resolved.slice(-19), metrics.resolved],
    }))
  }, [metrics.new, metrics.pending, metrics.progress, metrics.resolved])

  useEffect(() => {
    let handle: IdleHandle | null = null
    async function loadChart() {
      const Chart = (await import('chart.js/auto')).default
      const ctx = document.getElementById('trendsChart') as HTMLCanvasElement | null
      if (!ctx) return
      trendChart.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: Array.from({ length: 12 }, (_, i) => `${i}`),
          datasets: [
            {
              label: 'Novos',
              data: [],
              borderColor: '#1e40af',
              backgroundColor: 'rgba(30,64,175,0.1)',
              fill: true,
            },
            {
              label: 'Resolvidos',
              data: [],
              borderColor: '#059669',
              backgroundColor: 'rgba(5,150,105,0.1)',
              fill: true,
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      })
    }
    handle = scheduleIdleCallback(loadChart)
    return () => {
      if (handle !== null) cancelIdleCallback(handle)
      trendChart.current?.destroy()
    }
  }, [])

  useEffect(() => {
    if (filters) {
      queryClient.invalidateQueries({ queryKey: ['metrics-aggregated'] })
    }
  }, [filters, queryClient])

  const refreshMetrics = () =>
    queryClient.invalidateQueries({ queryKey: ['metrics-aggregated'] })

  return {
    metrics,
    sparkRefs,
    history,
    refreshMetrics,
    isLoading: query.isLoading,
    error: query.error as Error | null,
  }
}
