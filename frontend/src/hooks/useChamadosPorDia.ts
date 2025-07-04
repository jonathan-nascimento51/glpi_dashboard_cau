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
    { refreshInterval: 60000 },
  )

  const dados = (data ?? []).map((d) => ({
    date: d.date,
    total: Number(d.total),
  }))

  return { dados, error, isLoading }
}
