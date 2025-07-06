import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface Metrics {
  total: number
  opened: number
  closed: number
}

export function useTicketMetrics() {
  return useQuery<Metrics>(['metrics'], () => fetcher('/metrics'))
}
