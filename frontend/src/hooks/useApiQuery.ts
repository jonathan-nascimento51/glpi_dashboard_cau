import { useQuery, type QueryKey, type UseQueryOptions } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export function useApiQuery<TData, TError = Error>(
  queryKey: QueryKey,
  endpoint: string,
  options: Omit<UseQueryOptions<TData, TError, TData, QueryKey>, 'queryKey' | 'queryFn'> = {},
) {
  return useQuery<TData, TError>({
    queryKey,
    queryFn: () => fetcher<TData>(endpoint),
    ...options,
  })
}
