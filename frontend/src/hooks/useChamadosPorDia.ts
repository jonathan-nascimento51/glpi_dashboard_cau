import useSWR from 'swr'
import { fetcher } from '../lib/swrClient'

export interface ChamadoPorDia {
  date: string
  total: number
}

export function useChamadosPorDia() {
  const { data, error, isLoading } = useSWR<ChamadoPorDia[]>(
    '/chamados/por-dia',
    fetcher,
    { refreshInterval: 60000, revalidateOnFocus: false },
  )

  return {
    dados: data || [],
    loading: isLoading,
    erro: error,
  }
}
