import { useApiQuery } from './useApiQuery'
import type { ChamadoPorDia } from '../types/chamado'

export function useChamadosPorDia() {
  const query = useApiQuery<ChamadoPorDia[], Error>(
    '/chamados/por-dia',
    undefined,
    {
      select: (data: ChamadoPorDia[]) =>
        data.map((d) => ({ date: d.date, total: Number(d.total) })),
      refetchInterval: 60000,
    },
  )

  return {
    data: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
