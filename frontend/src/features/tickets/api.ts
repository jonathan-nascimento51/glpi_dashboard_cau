import { useApiQuery } from '@/hooks/useApiQuery'

export interface Metrics {
  total: number
  opened: number
  closed: number
}

export function useTicketMetrics() {
  return useApiQuery<Metrics>(['metrics'], '/metrics')
}
