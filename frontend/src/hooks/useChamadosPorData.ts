import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['chamados', 'por-data'],
    queryFn: () => fetcher<ChamadoPorData[]>('/chamados/por-data'),
    refetchInterval: 60000,
  })

  const dados = (data ?? []).map((d) => ({
    date: d.date,
    total: Number(d.total),
  }))

  return { dados, error, isLoading }
}
