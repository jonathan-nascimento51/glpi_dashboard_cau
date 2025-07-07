import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface Ticket {
  id: number | string
  name: string
  [key: string]: any
}

export function useTickets() {
  const queryClient = useQueryClient()
  const query = useQuery<Ticket[], Error>({
    queryKey: ['tickets'],
    queryFn: () => fetcher('/tickets'),
  })

  const refreshTickets = () =>
    queryClient.invalidateQueries({ queryKey: ['tickets'] })

  return {
    tickets: query.data,
    error: query.error as Error | null,
    isLoading: query.isLoading,
    refreshTickets,
  }
}
