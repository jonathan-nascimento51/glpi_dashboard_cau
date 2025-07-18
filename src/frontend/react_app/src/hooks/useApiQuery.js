import { useQuery } from '@tanstack/react-query';
import { fetcher } from '@/lib/swrClient';
export function useApiQuery(queryKey, endpoint, options = {}) {
    const { init, ...queryOptions } = options;
    return useQuery({
        queryKey,
        queryFn: () => fetcher(endpoint, init),
        ...queryOptions,
    });
}
