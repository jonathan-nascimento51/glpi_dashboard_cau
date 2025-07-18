import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from '@/hooks/useApiQuery';
export function useTickets() {
    const queryClient = useQueryClient();
    const query = useApiQuery(['tickets'], '/tickets');
    const refreshTickets = () => queryClient.invalidateQueries({ queryKey: ['tickets'] });
    return {
        tickets: query.data,
        error: query.error,
        isLoading: query.isLoading,
        refreshTickets,
    };
}
