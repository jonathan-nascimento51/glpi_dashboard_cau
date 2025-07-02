import { useQuery } from '@tanstack/react-query'
import type { Metrics } from '../../entities/metrics'

export function useTicketMetrics() {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: async (): Promise<Metrics> => {
      const res = await fetch('/metrics')
      if (!res.ok) {
        throw new Error('Failed to fetch metrics')
      }
      return res.json() as Promise<Metrics>
    },
  })
}
