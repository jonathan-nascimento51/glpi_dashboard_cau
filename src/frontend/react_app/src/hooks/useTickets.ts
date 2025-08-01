import { useEffect, useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useApiQuery } from '../hooks/useApiQuery'
import type { FiltersState } from './useFilters'
import { buildQueryString, FilterQuery } from '../lib/buildQueryString'
import { stableStringify } from '../lib/stableStringify'
import type { CleanTicketDTO } from '../types/api'
import type { Ticket } from '../types/ticket'

function toTicket(dto: CleanTicketDTO): Ticket {
  return {
    ...dto,
    status: dto.status != null ? String(dto.status) : undefined,
    priority: dto.priority != null ? String(dto.priority) : undefined,
    name: dto.name ?? "",
    requester: dto.requester ?? undefined,
    // Prefer `undefined` over `null` when the API omits the field
    date_creation:
      dto.date_creation != null ? new Date(dto.date_creation) : undefined,
  }
}

export function useTickets(filters?: FiltersState) {
  const queryClient = useQueryClient()
  const qs = buildQueryString(filters as FilterQuery | undefined)
  const serialized = stableStringify(filters as Record<string, unknown> | undefined)
  const query = useApiQuery<CleanTicketDTO[]>(
    ['tickets', serialized],
    `/v1/tickets${qs}`,
  )
  const tickets = useMemo(() => query.data?.map(toTicket), [query.data])

  useEffect(() => {
    if (filters) {
      queryClient.invalidateQueries({ queryKey: ['tickets', serialized] })
    }
  }, [filters, queryClient])

  const refreshTickets = () =>
    queryClient.invalidateQueries({ queryKey: ['tickets', serialized] })

  return {
    tickets,
    error: query.error,
    isLoading: query.isLoading,
    isSuccess: query.isSuccess,
    refreshTickets,
  }
}
