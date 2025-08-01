import { useApiQuery } from './useApiQuery'
import type { Ticket } from '../types/ticket'

export interface SearchResult extends Pick<Ticket, 'id' | 'name' | 'requester'> {}

export function useSearch(term: string) {
  const query = term.trim()
  return useApiQuery<SearchResult[]>(
    ['search', query],
    `v1/tickets/search?query=${encodeURIComponent(query)}`,
    {
      enabled: query.length > 0,
    },
  )
}
