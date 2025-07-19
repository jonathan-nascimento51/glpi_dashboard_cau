// Hook para buscar chamados agrupados por data usando React Query v5
// Deve usar staleTime para evitar refetching desnecessário
// Deve ativar refetch automático ao focar a janela
// Pode incluir refetchInterval para polling se necessário

import { useQuery } from '@tanstack/react-query'
import { fetchChamadosPorData } from '../services/api'

/**
 * Hook to fetch "chamados" grouped by date using React Query v5.
 * 
 * This hook leverages caching to minimize unnecessary refetching and supports
 * automatic refetching when the window regains focus. It can also be configured
 * for polling by uncommenting the `refetchInterval` option.
 * 
 * @returns {import('@tanstack/react-query').UseQueryResult} - The result object from React Query, 
 * including the fetched data, loading state, and error information.
 * 
 * @example
 * import { useChamadosPorData } from './hooks/useChamadosPorData';
 * 
 * function ChamadosComponent() {
 *   const { data, isLoading, error } = useChamadosPorData();
 * 
 *   if (isLoading) return <p>Loading...</p>;
 *   if (error) return <p>Error: {error.message}</p>;
 * 
 *   return (
 *     <ul>
 *       {data.map(chamado => (
 *         <li key={chamado.id}>{chamado.name}</li>
 *       ))}
 *     </ul>
 *   );
 * }
 */
export function useChamadosPorData() {
  return useQuery({
    queryKey: ['chamados-por-data'],
    queryFn: fetchChamadosPorData,
    staleTime: 1000 * 60 * 5, // 5 minutos
    gcTime: 1000 * 60 * 10, // 10 minutos
    refetchOnWindowFocus: true,
    // refetchInterval: 30000, // descomente para polling a cada 30s
  })
}
