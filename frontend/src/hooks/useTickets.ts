import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface Ticket {
  id: number | string
  name: string
  [key: string]: any
}

export function useTickets() {
  const queryClient = useQueryClient()
  const { data, error, isLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => fetcher<Ticket[]>('/tickets'),
  })

  return {
    tickets: data,
    error,
    isLoading,
    refreshTickets: () => queryClient.invalidateQueries({ queryKey: ['tickets'] }),
  }
}
