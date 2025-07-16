import { useApiQuery } from '@/hooks/useApiQuery'
import type { ChamadoPorDia } from '../types/chamado'

export function useChamadosPorDia() {
  const query = useApiQuery<ChamadoPorDia[], Error>(
    ['chamados-por-dia'],
    '/chamados/por-dia',
    {
      select: (data: ChamadoPorDia[]) =>
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
