import { useApiQuery } from '@/hooks/useApiQuery';
export function useChamadosPorData() {
    const query = useApiQuery(['chamados-por-data'], '/chamados/por-data', {
        select: (data) => data.map((d) => ({ date: d.date, total: Number(d.total) })),
        refetchInterval: 60000,
    });
    return {
        dados: query.data ?? [],
        // Se você não tiver um tipo ApiError:
        error: query.error
            ? query.error.status === 503 // Use 'any' temporariamente
                ? new Error('Serviço temporariamente indisponível. Tente novamente mais tarde.')
                : query.error
            : null,
        isLoading: query.isLoading,
    };
}
