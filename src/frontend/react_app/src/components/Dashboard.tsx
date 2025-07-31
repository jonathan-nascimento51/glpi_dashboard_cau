import type { LevelMetrics } from '../types/metricsOverview'
import { useMetricsOverview } from '../hooks/useMetricsOverview'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'

interface MetricCardProps {
  level: string
  data: LevelMetrics
}

function MetricCard({ level, data }: MetricCardProps) {
  return (
    <div
      className="metric-card flex flex-col items-start justify-between cursor-pointer transition-all"
      data-testid={`card-${level}`}
    >
      <div className="metric-header flex items-center gap-2 mb-2">
        <span className="metric-icon new">
          <i className="fas fa-layer-group" />
        </span>
        <h3 className="metric-label text-lg font-semibold">{level}</h3>
      </div>
      <div className="metric-value text-3xl font-bold mb-1">{data.open}</div>
      <div className="metric-change positive">
        <i className="fas fa-arrow-up" /> {data.closed} fechados
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { metrics, isLoading, isError, error, refreshMetrics } = useMetricsOverview()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (isError) {
    return (
      <ErrorMessage
        message={error?.message ?? 'Não foi possível carregar as métricas. Tente novamente mais tarde.'}
        onRetry={refreshMetrics}
      />
    )
  }

  return (
    <div className="dashboard grid gap-4 sm:grid-cols-2 md:grid-cols-4" data-testid="dashboard">
      {metrics && Object.entries(metrics).map(([level, data]) => (
        <MetricCard key={level} level={level} data={data} />
      ))}
    </div>
  )
}
