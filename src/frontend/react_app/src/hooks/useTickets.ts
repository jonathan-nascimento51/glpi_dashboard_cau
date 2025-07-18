import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from '@/hooks/useApiQuery'
import type { Ticket } from '../types/ticket.js'

export function useTickets() {
  const queryClient = useQueryClient()
  const query = useApiQuery<Ticket[], Error>([
    'tickets',
  ], '/tickets', {
    select: (data: Ticket[]) =>
      data.map((t) => ({
        ...t,
        solvedate: t.solvedate,
        closedate: t.closedate,
      })),
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
