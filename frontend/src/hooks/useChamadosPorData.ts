import { useQuery } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

async function fetchChamadosPorData(): Promise<ChamadoPorData[]> {
  return fetcher('/chamados/por-data')
}

export function useChamadosPorData() {
  const query = useQuery<ChamadoPorData[], Error>({
    queryKey: ['chamados-por-data'],
    queryFn: fetchChamadosPorData,
    select: (data: ChamadoPorData[]) =>
      data.map((d) => ({ date: d.date, total: Number(d.total) })),
    refetchInterval: 60000,
  })

  return {
    dados: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
