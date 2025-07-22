import { useState, useEffect } from "react";
import axios, { AxiosError } from "axios";

interface ApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

export function useApiQuery<T>(endpoint: string): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    if (!endpoint) {
      setState({ data: null, isLoading: false, error: "Endpoint não fornecido." });
      return;
    }

    const controller = new AbortController();

    const fetchData = async () => {
      setState({ data: null, isLoading: true, error: null });
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
        if (!baseUrl) {
          throw new Error("URL base da API não configurada. Verifique NEXT_PUBLIC_API_BASE_URL.");
        }
        const response = await axios.get<T>(`${baseUrl}${endpoint}`, { signal: controller.signal });
        setState({ data: response.data, isLoading: false, error: null });
      } catch (err) {
        if (axios.isCancel(err)) {
          console.log("Requisição cancelada:", err.message);
          return;
        }
        const error = err as AxiosError;
        console.error(`Erro ao buscar de ${endpoint}:`, error);
        const errorMessage = (error.response?.data as any)?.detail || error.message || "Ocorreu um erro desconhecido.";
        setState({ data: null, isLoading: false, error: String(errorMessage) });
      }
    };

    fetchData();

    return () => controller.abort();
  }, [endpoint]);

  return state;
}
