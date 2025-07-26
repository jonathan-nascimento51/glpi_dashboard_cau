import { useMetricsOverview } from '../hooks/useMetricsOverview'
import { LevelsPanel } from './LevelsPanel'

export interface LevelMetrics {
  progress: number
  pending: number
  // Outras propriedades...
}

export default function LevelsSection() {
  const { metrics } = useMetricsOverview()
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
      <LevelsPanel levels={levels} />
    </section>
  )
}
