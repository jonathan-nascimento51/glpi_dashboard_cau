import { useMemo } from 'react'
import {
  useQuery,
  type QueryKey,
  type UseQueryOptions,
  type UseQueryResult,
} from '@tanstack/react-query'

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`;
  }
  const keys = Object.keys(value as Record<string, unknown>).sort();
  const entries = keys.map(
    (key) =>
      `${JSON.stringify(key)}:${stableStringify(
        (value as Record<string, unknown>)[key]
      )}`
  );
  return `{${entries.join(',')}}`;
}

export function useApiQuery<T>(
  queryKey: QueryKey,
  endpoint: string,
  options?: UseQueryOptions<T, Error>,
): UseQueryResult<T, Error> {
  const memoizedOptions = useMemo(
    () => (options ? { ...options, serialized: stableStringify(options as Record<string, unknown>) } : {}),
    [options],
  );

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  const fetchFromApi = async (): Promise<T> => {
    if (!baseUrl) {
      throw new Error(
        'URL base da API não configurada. Verifique NEXT_PUBLIC_API_BASE_URL.',
      );
    }
    const response = await fetch(`${baseUrl}${endpoint}`);
    if (!response.ok) {
      let errorMessage = `Erro na requisição: ${response.statusText}`;
      try {
        const errorBody = await response.json();
        if (errorBody && (errorBody.message || errorBody.error)) {
          errorMessage += ` - ${errorBody.message || errorBody.error}`;
        }
      } catch {
        // ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    return (await response.json()) as T;
  };

  return useQuery<T, Error>({
    queryKey: Array.isArray(queryKey) ? queryKey : [queryKey],
    queryFn: fetchFromApi,
    ...(options ?? {}),
    meta: { serializedOpts },
  });
}
