import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorDia {
  date: string
  total: number
}

export function useChamadosPorDia() {
  const query = useQuery<ChamadoPorDia[], Error>({
    queryKey: ['chamados-por-dia'],
    queryFn: () => fetcher('/chamados/por-dia'),
    select: (data: ChamadoPorDia[]) =>
      data.map((d) => ({ date: d.date, total: Number(d.total) })),
    refetchInterval: 60000,
  })

  return {
    dados: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
