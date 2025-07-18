import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from '@/hooks/useApiQuery.js'
import { useMemo } from 'react'
import type { CleanTicketDTO } from '../types/api.js'
import type { Ticket } from '../types/ticket.js'

function toTicket(dto: CleanTicketDTO): Ticket {
  return {
    ...dto,
    date_creation: dto.date_creation ? new Date(dto.date_creation) : null,
  }
}

export function useTickets() {
  const queryClient = useQueryClient()
  const query = useApiQuery<CleanTicketDTO[], Error>(['tickets'], '/tickets')
  const tickets = useMemo(() => query.data?.map(toTicket), [query.data])

  const refreshTickets = () =>
    queryClient.invalidateQueries({ queryKey: ['tickets'] })

  return {
    tickets,
    error: query.error as Error | null,
    isLoading: query.isLoading,
    refreshTickets,
  }
}
