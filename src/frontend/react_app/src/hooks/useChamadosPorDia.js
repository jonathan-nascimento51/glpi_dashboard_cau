import { useApiQuery } from '@/hooks/useApiQuery';
export function useChamadosPorDia() {
    const query = useApiQuery(['chamados-por-dia'], '/chamados/por-dia', {
        select: (data) => data.map((d) => ({ date: d.date, total: Number(d.total) })),
        refetchInterval: 60000,
    });
    return {
        dados: query.data ?? [],
        error: query.error,
        isLoading: query.isLoading,
    };
}
