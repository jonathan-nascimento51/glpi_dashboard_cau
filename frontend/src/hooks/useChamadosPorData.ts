import { useApiQuery } from './useApiQuery'
import type { ChamadoPorData } from '../types/chamado'

export function useChamadosPorData() {
  const query = useApiQuery<ChamadoPorData[], Error>(
    ['chamados-por-data'],
    '/chamados/por-data',
    {
      select: (data: ChamadoPorData[]) =>
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
