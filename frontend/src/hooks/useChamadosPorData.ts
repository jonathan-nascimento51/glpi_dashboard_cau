import useSWR from 'swr'
import { fetcher } from '../lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const { data, error, isLoading } = useSWR<ChamadoPorData[]>(
    '/chamados/por-data',
    fetcher,
    { refreshInterval: 60000, revalidateOnFocus: false },
  )

  return {
    dados: data || [],
    loading: isLoading,
    erro: error,
  }
}
