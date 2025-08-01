import { useApiQuery } from './useApiQuery'
import type { ChamadoPorDia } from '../types/chamado'

export function useChamadosPorDia() {
  const query = useApiQuery<ChamadoPorDia[]>(['chamados-por-dia'], '/v1/chamados/por-dia', {
    refetchInterval: 60000,
  })

  return {
    data: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
