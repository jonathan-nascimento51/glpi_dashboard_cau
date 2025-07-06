import useSWR from 'swr'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const { data, error, isLoading } = useSWR<ChamadoPorData[]>(
    '/chamados/por-data',
    fetcher,
    { refreshInterval: 60000 },
  )

  const dados = (data ?? []).map((d) => ({
    date: d.date,
    total: Number(d.total),
  }))

  return { dados, error, isLoading }
}
