import useSWR from 'swr'
import { fetcher } from '../lib/swrClient'

export interface Ticket {
  id: number | string
  name: string
  [key: string]: any
}

export function useTickets() {
  const { data, error, isLoading, mutate } = useSWR<Ticket[]>('/tickets', fetcher)

  return {
    tickets: data,
    error,
    isLoading,
    refreshTickets: mutate,
  }
}
