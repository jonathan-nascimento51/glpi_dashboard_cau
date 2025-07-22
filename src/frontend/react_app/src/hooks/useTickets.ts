import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from '../hooks/useApiQuery'
import { useMemo } from 'react'
import type { CleanTicketDTO } from '../types/api'
import type { Ticket } from '../types/ticket'

function toTicket(dto: CleanTicketDTO): Ticket {
  return {
    ...dto,
    status: dto.status != null ? String(dto.status) : undefined,
    priority: dto.priority != null ? String(dto.priority) : undefined,
    name: dto.name ?? "",
    // Prefer `undefined` over `null` when the API omits the field
    date_creation:
      dto.date_creation != null ? new Date(dto.date_creation) : undefined,
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
    error: query.error,
    isLoading: query.isLoading,
    isSuccess: query.isSuccess,
    refreshTickets,
  }
}
