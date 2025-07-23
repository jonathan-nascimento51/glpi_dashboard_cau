import { renderHook, waitFor } from '@testing-library/react';
import { useApiQuery } from '../../src/hooks/useApiQuery';

const fetchMock = jest.fn();
global.fetch = fetchMock as unknown as typeof fetch;

const MOCK_API_URL = 'http://test-api.com';
process.env.NEXT_PUBLIC_API_BASE_URL = MOCK_API_URL;

describe('useApiQuery', () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it('deve retornar o estado de carregamento inicialmente', () => {
    const { result } = renderHook(() => useApiQuery('/tickets'));
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('deve buscar os dados com sucesso e atualizar o estado', async () => {
    const mockData = { tickets: [{ id: 1, name: 'Test Ticket' }] };
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response);

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(`${MOCK_API_URL}/tickets`, expect.objectContaining({ signal: expect.any(Object) }));
  });

  it('deve tratar erros de busca e atualizar o estado', async () => {
    const errorMessage = 'Network Error';
    fetchMock.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('não deve fazer a busca se o endpoint estiver vazio', () => {
    const { result } = renderHook(() => useApiQuery(''));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Endpoint não fornecido.');
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('deve tratar erro de URL base não configurada', async () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe('URL base da API não configurada. Verifique NEXT_PUBLIC_API_BASE_URL.');

    process.env.NEXT_PUBLIC_API_BASE_URL = MOCK_API_URL;
  });
});
