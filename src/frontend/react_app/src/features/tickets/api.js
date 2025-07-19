import { useApiQuery } from '@/hooks/useApiQuery';
export function useTicketMetrics() {
    return useApiQuery(['metrics'], '/metrics');
}
