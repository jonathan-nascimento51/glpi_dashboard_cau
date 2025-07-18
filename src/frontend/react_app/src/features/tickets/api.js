import { useApiQuery } from '@/hooks/useApiQuery.js';
export function useTicketMetrics() {
    return useApiQuery(['metrics'], '/metrics');
}
