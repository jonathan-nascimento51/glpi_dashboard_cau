import { useApiQuery } from '../../hooks/useApiQuery'
import type { TicketMetrics } from '../../types/dashboard'

export function useTicketMetrics() {
  return useApiQuery<TicketMetrics>(['ticket-metrics'], '/metrics')
}
