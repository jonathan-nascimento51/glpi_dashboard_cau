import { useEffect, useRef } from 'react'
import type { Chart as ChartType } from 'chart.js'
import {
  scheduleIdleCallback,
  cancelIdleCallback,
  type IdleHandle,
} from '../lib/scheduleIdleCallback'

/**
 * Draws a tiny sparkline using Chart.js on the provided canvas.
 * The chart updates whenever the `data` array changes.
 */
export function useSparkline(
  canvasRef: React.RefObject<HTMLCanvasElement>,
  data: number[],
) {
  const chartRef = useRef<ChartType | null>(null)

  useEffect(() => {
    if (!canvasRef.current) return
    let handle: IdleHandle | null = null
    async function render() {
      const Chart = (await import('chart.js/auto')).default
      const ctx = canvasRef.current
      if (!ctx) return
      if (!chartRef.current) {
        chartRef.current = new Chart(ctx, {
          type: 'line',
          data: { labels: data.map((_, i) => String(i)), datasets: [{ data }] },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { x: { display: false }, y: { display: false } },
            elements: { point: { radius: 0 } },
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
          },
        })
      } else {
        chartRef.current.data.labels = data.map((_, i) => String(i))
        chartRef.current.data.datasets[0].data = data
        chartRef.current.update()
      }
    }
    handle = scheduleIdleCallback(render)
    return () => {
      if (handle !== null) cancelIdleCallback(handle)
    }
  }, [canvasRef, data])

  useEffect(() => {
    return () => chartRef.current?.destroy()
  }, [chartRef.current])
}
