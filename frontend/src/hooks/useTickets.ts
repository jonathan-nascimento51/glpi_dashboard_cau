import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from './useApiQuery'

export interface Ticket {
  id: number | string
  name: string
  [key: string]: any
}

export function useTickets() {
  const queryClient = useQueryClient()
  const query = useApiQuery<Ticket[], Error>(['tickets'], '/tickets')

  const refreshTickets = () =>
    queryClient.invalidateQueries({ queryKey: ['tickets'] })

  return {
    tickets: query.data,
    error: query.error as Error | null,
    isLoading: query.isLoading,
    refreshTickets,
  }
}
