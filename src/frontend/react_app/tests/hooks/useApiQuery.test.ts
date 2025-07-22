import { renderHook, waitFor } from '@testing-library/react';
import axios from 'axios';
import { useApiQuery } from '../../src/hooks/useApiQuery';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const MOCK_API_URL = 'http://test-api.com';
process.env.NEXT_PUBLIC_API_BASE_URL = MOCK_API_URL;

describe('useApiQuery', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
  });

  it('deve retornar o estado de carregamento inicialmente', () => {
    const { result } = renderHook(() => useApiQuery('/tickets'));
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('deve buscar os dados com sucesso e atualizar o estado', async () => {
    const mockData = { tickets: [{ id: 1, name: 'Test Ticket' }] };
    mockedAxios.get.mockResolvedValue({ data: mockData });

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(mockedAxios.get).toHaveBeenCalledWith(`${MOCK_API_URL}/tickets`, expect.any(Object));
  });

  it('deve tratar erros de busca e atualizar o estado', async () => {
    const errorMessage = 'Network Error';
    mockedAxios.get.mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('não deve fazer a busca se o endpoint estiver vazio', () => {
    const { result } = renderHook(() => useApiQuery(''));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Endpoint não fornecido.');
    expect(mockedAxios.get).not.toHaveBeenCalled();
  });

  it('deve tratar erro de URL base não configurada', async () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    const { result } = renderHook(() => useApiQuery('/tickets'));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.error).toBe('URL base da API não configurada. Verifique NEXT_PUBLIC_API_BASE_URL.');

    process.env.NEXT_PUBLIC_API_BASE_URL = MOCK_API_URL;
  });
});
