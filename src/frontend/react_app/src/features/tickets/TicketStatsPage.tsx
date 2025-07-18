import { useTicketMetrics } from './api.js'
import { StatsCard } from '../../widgets/stats/StatsCard.js'

export function TicketStatsPage() {
  const { data, isLoading, error } = useTicketMetrics()

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>{(error as Error).message}</div>

  return (
    <div className="grid gap-4 grid-cols-3">
      <StatsCard label="Total" value={data!.total} />
      <StatsCard label="Opened" value={data!.opened} />
      <StatsCard label="Closed" value={data!.closed} />
    </div>
  )
}
