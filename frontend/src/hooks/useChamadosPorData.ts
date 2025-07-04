import useSWR from 'swr/core'
import { fetcher } from '../lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const { data, error, isLoading } = useSWR<ChamadoPorData[]>('/chamados/por-data', fetcher)

  return {
    dados: data,
    error,
    isLoading,
  }
}
