import { useApiQuery } from '@/hooks/useApiQuery'
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
    // Se você não tiver um tipo ApiError:
    error: query.error
      ? (query.error as any).status === 503  // Use 'any' temporariamente
        ? new Error('Serviço temporariamente indisponível. Tente novamente mais tarde.')
        : (query.error as Error)
      : null,
    isLoading: query.isLoading,
  }
}
