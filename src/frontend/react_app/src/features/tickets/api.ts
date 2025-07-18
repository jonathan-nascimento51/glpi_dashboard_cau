import { useApiQuery } from '@/hooks/useApiQuery.js'
import type { TicketMetrics } from '../../types/dashboard.js'

export function useTicketMetrics() {
  return useApiQuery<TicketMetrics, Error>(['metrics'], '/metrics')
}
