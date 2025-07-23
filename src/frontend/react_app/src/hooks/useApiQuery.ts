import { useMemo } from 'react'
import {
  useQuery,
  type UseQueryResult,
  type UseQueryOptions,
  type QueryKey,
} from '@tanstack/react-query'
import { fetcher } from '../lib/swrClient'
import { stableStringify } from '../lib/stableStringify'

function getBaseUrl(): string | undefined {
  return process.env.NEXT_PUBLIC_API_BASE_URL
}

export function useApiQuery<TData = unknown, TError = unknown>(
  queryKey: QueryKey,
  endpoint: string,
  options: Omit<UseQueryOptions<TData, TError>, 'queryKey' | 'queryFn'> = {},
): UseQueryResult<TData, TError> {
  const baseUrl = getBaseUrl()

  const key = useMemo(
    () =>
      Array.isArray(queryKey)
        ? queryKey.map((k) =>
            typeof k === 'object'
              ? stableStringify(k as Record<string, unknown>)
              : k,
          )
        : [queryKey],
    [queryKey],
  )

  return useQuery<TData, TError>({
    queryKey: key,
    ...options,
    enabled: options.enabled ?? true,
    queryFn: async ({ signal }) => {
      if (!endpoint) {
        throw new Error('Endpoint not provided.')
      }
      if (!baseUrl) {
        throw new Error(
          'API base URL not configured. Check NEXT_PUBLIC_API_BASE_URL.',
        )
      }

      const controller = new AbortController()
      const abort = () => controller.abort()

      if (signal) {
        if (signal.aborted) abort()
        else signal.addEventListener('abort', abort)
      }

      try {
        return await fetcher<TData>(
          endpoint,
          { signal: controller.signal },
          { baseUrl },
        )
      } finally {
        if (signal) signal.removeEventListener('abort', abort)
      }
    },
  })
}
