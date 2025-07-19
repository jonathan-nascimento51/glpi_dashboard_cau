// Hook para buscar chamados agrupados por data usando React Query v5
// Deve usar staleTime para evitar refetching desnecessário
// Deve ativar refetch automático ao focar a janela
// Pode incluir refetchInterval para polling se necessário

import { useQuery } from '@tanstack/react-query'
import { fetchChamadosPorData } from '../services/api'

export function useChamadosPorData() {
  return useQuery(['chamados-por-data'], fetchChamadosPorData, {
    staleTime: 1000 * 60 * 5, // 5 minutos
    gcTime: 1000 * 60 * 10, // 10 minutos
    refetchOnWindowFocus: true,
    // refetchInterval: 30000, // descomente para polling a cada 30s
  })
}
