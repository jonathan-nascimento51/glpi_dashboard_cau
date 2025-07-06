import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const query = useQuery<ChamadoPorData[]>(
    ['chamados-por-data'],
    () => fetcher('/chamados/por-data'),
    {
      select: (data) =>
        data.map((d) => ({ date: d.date, total: Number(d.total) })),
      refetchInterval: 60000,
    },
  )

  return {
    dados: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
