import { useApiQuery } from './useApiQuery'
import type { ChamadoPorDia } from '../types/chamado'

export function useChamadosPorDia() {
  const query = useApiQuery<ChamadoPorDia[], Error>(['chamados-por-dia'], '/chamados/por-dia', {
    // Renomeia 'count' para 'total' para ser consumido pelo componente de gráfico,
    // que espera uma propriedade 'total'.
    select: (data: ChamadoPorDia[]) =>
      data.map((d) => ({ date: d.date, total: Number(d.count) })),
    refetchInterval: 60000,
  })

  return {
    data: query.data ?? [],
    error: query.error as Error | null,
    isLoading: query.isLoading,
  }
}
