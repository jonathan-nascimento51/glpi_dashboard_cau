'use client';

import { useEffect, useRef, useState } from 'react'
import { Chart } from 'chart.js/auto'

export interface Metrics {
  new: number
  pending: number
  progress: number
  resolved: number
}

export function useDashboardData() {
  const [metrics, setMetrics] = useState<Metrics>({
    new: 42,
    pending: 11,
    progress: 37,
    resolved: 64,
  })
  const trendChart = useRef<Chart | null>(null)
  const sparkRefs = {
    new: useRef<HTMLCanvasElement>(null),
    pending: useRef<HTMLCanvasElement>(null),
    progress: useRef<HTMLCanvasElement>(null),
    resolved: useRef<HTMLCanvasElement>(null),
  }

  useEffect(() => {
    const ctx = document.getElementById(
      'trendsChart',
    ) as HTMLCanvasElement | null
    if (!ctx) {
      return;
    }
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
    return () => trendChart.current?.destroy()
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((m) => ({
        new: m.new + Math.floor(Math.random() * 3 - 1),
        pending: m.pending + Math.floor(Math.random() * 3 - 1),
        progress: m.progress + Math.floor(Math.random() * 3 - 1),
        resolved: m.resolved + Math.floor(Math.random() * 3 - 1),
      }))
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return { metrics, sparkRefs }
}
