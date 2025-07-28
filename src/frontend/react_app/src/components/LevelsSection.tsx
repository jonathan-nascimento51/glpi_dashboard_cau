import { useMetricsOverview } from '../hooks/useMetricsOverview'
import { LevelsPanel } from './LevelsPanel'

export interface LevelMetrics {
  open: number
  closed: number
  progress?: number
  pending?: number
  // Outras propriedades...
}

export default function LevelsSection() {
  const { metrics, isLoading, error, refreshMetrics } = useMetricsOverview()
  const levels = metrics
    ? Object.entries(metrics).map(([name, data]) => ({
        name,
        metrics: {
          new: data.open,
          progress: data.progress ?? 0,
          pending: data.pending ?? 0,
          resolved: data.closed,
        },
      }))
    : []

  return (
    <section className="levels-section">
      <LevelsPanel
        levels={levels}
        isLoading={isLoading}
        error={error}
        onRetry={refreshMetrics}
      />
    </section>
  )
}
