import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { stableStringify } from '../lib/stableStringify';

/**
 * A custom hook to query the backend API.
 * It uses a stable query key to prevent unnecessary refetches.
 *
 * @param endpoint The API endpoint to query (e.g., '/tickets').
 * @param params Optional query parameters.
 * @param options Optional react-query options.
 * @returns The result of the useQuery hook.
 */

type ApiQueryKey = [string, string | undefined];

const fetchFromApi = async (endpoint: string, params?: Record<string, unknown>) => {
  // In a Vite environment, environment variables must be accessed via `import.meta.env`
  // and be prefixed with `VITE_` to be exposed to the client.
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const url = new URL(endpoint, baseUrl);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || 'Network response was not ok');
  }

  return response.json();
};

export const useApiQuery = <TData = unknown, TError = Error>(
  endpoint: string,
  params?: Record<string, unknown>,
  options?: Omit<UseQueryOptions<TData, TError, TData, ApiQueryKey>, 'queryKey' | 'queryFn'>
) => {
  const queryKey: ApiQueryKey = [endpoint, params ? stableStringify(params) : undefined];

  return useQuery<TData, TError, TData, ApiQueryKey>({
    queryKey,
    queryFn: () => fetchFromApi(endpoint, params),
    ...options,
  });
};
