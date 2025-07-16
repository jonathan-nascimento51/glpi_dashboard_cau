import { useQuery, type QueryKey, type UseQueryOptions } from '@tanstack/react-query'
import { fetcher } from '@/lib/swrClient'

export function useApiQuery<TData = unknown, TError = Error>(
  queryKey: QueryKey,
  endpoint: string,
  options: Omit<UseQueryOptions<TData, TError, TData, QueryKey>, 'queryKey' | 'queryFn'> & { init?: RequestInit } = {},
) {
  const { init, ...queryOptions } = options
  return useQuery<TData, TError>({
    queryKey,
    queryFn: () => fetcher<TData>(endpoint, init),
    ...queryOptions,
  })
}
