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
    <div className="border rounded p-4 shadow flex-1 min-w-[200px]" data-testid={`card-${level}`}>
      <h3 className="text-lg font-semibold mb-2">Nível {level}</h3>
      <p>Abertos: {data.open}</p>
      <p>Fechados: {data.closed}</p>
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
