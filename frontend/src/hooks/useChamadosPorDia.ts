import useSWR from 'swr/core'
import { fetcher } from '../lib/swrClient'

export interface ChamadoPorDia {
  date: string
  total: number
}

export function useChamadosPorDia() {
  const { data, error, isLoading } = useSWR<ChamadoPorDia[]>('/chamados/por-dia', fetcher)

  return {
    dados: data,
    error,
    isLoading,
  }
}
