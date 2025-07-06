import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorDia {
  date: string
  total: number
}

export function useChamadosPorDia() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['chamados', 'por-dia'],
    queryFn: () => fetcher<ChamadoPorDia[]>('/chamados/por-dia'),
    refetchInterval: 60000,
  })

  const dados = (data ?? []).map((d) => ({
    date: d.date,
    total: Number(d.total),
  }))

  return { dados, error, isLoading }
}
