import { useState, useEffect } from "react";

interface ApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

const stableStringify = (value: unknown) =>
  JSON.stringify(value, Object.keys(value as Record<string, unknown>).sort());

export function useApiQuery<T>(
  endpoint: string,
  options?: RequestInit,
): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    isLoading: true,
    error: null,
  });
  const stableOptions = options ? stableStringify(options) : '';

  useEffect(() => {
    if (!endpoint) {
      setState({ data: null, isLoading: false, error: 'Endpoint não fornecido.' });
      return;
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!baseUrl) {
      setState({
        data: null,
        isLoading: false,
        error: 'URL base da API não configurada. Verifique NEXT_PUBLIC_API_BASE_URL.',
      });
      return;
    }

    const controller = new AbortController();

    const fetchData = async () => {
      setState({ data: null, isLoading: true, error: null });
      try {
        const response = await fetch(`${baseUrl}${endpoint}`, {
          signal: controller.signal,
          ...options,
        });

        if (!response.ok) {
          let errorMessage = `Erro na requisição: ${response.statusText}`;
          try {
            const errorBody = await response.json();
            if (errorBody && (errorBody.message || errorBody.error)) {
              errorMessage += ` - ${errorBody.message || errorBody.error}`;
            }
          } catch (e) {
            // Falha ao fazer parse do corpo de erro, manter mensagem padrão
          }
          throw new Error(errorMessage);
        }

        const json = (await response.json()) as T;
        setState({ data: json, isLoading: false, error: null });
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Requisição cancelada:', err.message);
          return;
        }
        console.error(`Erro ao buscar de ${endpoint}:`, err);
        setState({
          data: null,
          isLoading: false,
          error: err.message ?? 'Ocorreu um erro desconhecido.',
        });
      }
    };

    fetchData();

    return () => controller.abort();
  }, [endpoint, stableOptions]);

  return state;
}
