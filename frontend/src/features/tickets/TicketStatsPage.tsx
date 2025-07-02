import { useTicketMetrics } from './api'
import { StatsCard } from '../../widgets/stats/StatsCard'
import { Loading } from '../../shared/Loading'
import type { Metrics } from '../../entities/metrics'

export function TicketStatsPage() {
  const { data, isLoading, error } = useTicketMetrics()
  const metrics = data as Metrics | undefined

  if (isLoading) return <Loading />
  if (error) return <div>Error loading metrics</div>

  return (
    <div className="grid gap-4 grid-cols-3">
      <StatsCard label="Total" value={metrics?.total ?? 0} />
      <StatsCard label="Opened" value={metrics?.opened ?? 0} />
      <StatsCard label="Closed" value={metrics?.closed ?? 0} />
    </div>
  )
}
