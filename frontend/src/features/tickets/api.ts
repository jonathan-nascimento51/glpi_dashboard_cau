import { useQuery } from '@tanstack/react-query'

export interface Metrics {
  total: number
  opened: number
  closed: number
}

export function useTicketMetrics() {
  return useQuery<Metrics>(['metrics'], async () => {
    const res = await fetch('/metrics')
    if (!res.ok) {
      throw new Error('Failed to fetch metrics')
    }
    return res.json() as Promise<Metrics>
  })
}
