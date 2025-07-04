'use client';

import { useEffect, useRef } from 'react'
import useSWR from 'swr'
import { fetcher } from '../lib/swrClient'
import type { Chart as ChartType } from 'chart.js'

export interface Metrics {
  new: number
  pending: number
  progress: number
  resolved: number
}

interface Aggregated {
  status: Record<string, number>
}

export function useDashboardData() {
  const { data, error, isLoading, mutate } = useSWR<Aggregated>(
    '/metrics/aggregated',
    fetcher,
  )

  const metrics: Metrics = {
    new: data?.status?.new ?? 0,
    pending: data?.status?.pending ?? 0,
    progress: data?.status?.progress ?? 0,
    resolved: data?.status?.resolved ?? 0,
  }
  const trendChart = useRef<ChartType | null>(null)
  const sparkRefs = {
    new: useRef<HTMLCanvasElement>(null),
    pending: useRef<HTMLCanvasElement>(null),
    progress: useRef<HTMLCanvasElement>(null),
    resolved: useRef<HTMLCanvasElement>(null),
  }

  useEffect(() => {
    let chartModule: typeof import('chart.js/auto') | null = null
    async function loadChart() {
      chartModule = await import('chart.js/auto')
      const ctx = document.getElementById(
        'trendsChart',
      ) as HTMLCanvasElement | null
      if (!ctx) {
        return
      }
      trendChart.current = new chartModule.Chart(ctx, {
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
    loadChart()
    return () => trendChart.current?.destroy()
  }, [])

  useEffect(() => {
    const id = setInterval(() => {
      mutate().catch(() => undefined)
    }, 30000)
    return () => clearInterval(id)
  }, [mutate])

  const refreshMetrics = () => mutate()

  return { metrics, sparkRefs, refreshMetrics, isLoading, error }
}
