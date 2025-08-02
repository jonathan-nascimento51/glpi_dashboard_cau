import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useApiQuery } from '../../src/hooks/useApiQuery'

const fetchMock = jest.fn()
global.fetch = fetchMock as unknown as typeof fetch

const MOCK_API_URL = 'http://test-api.com'
process.env.VITE_API_BASE_URL = MOCK_API_URL

let queryClient: QueryClient
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

beforeEach(() => {
  queryClient = new QueryClient()
})

describe('useApiQuery', () => {
  beforeEach(() => {
    fetchMock.mockReset()
  })

  it('deve iniciar em estado de carregamento', () => {
    const { result } = renderHook(() => useApiQuery(['tickets'], '/v1/tickets'), {
      wrapper,
    })
    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeNull()
  })

  it('deve buscar os dados com sucesso e atualizar o estado', async () => {
    const mockData = { tickets: [{ id: 1, name: 'Test Ticket' }] }
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockData,
    } as Response)

    const { result } = renderHook(() => useApiQuery(['tickets'], '/v1/tickets'), {
      wrapper,
    })

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.data).toEqual(mockData)
    expect(result.current.error).toBeNull()
    expect(fetchMock).toHaveBeenCalledWith(`${MOCK_API_URL}/v1/tickets`, expect.any(Object))
  })

  it('deve tratar erros de busca e atualizar o estado', async () => {
    const errorMessage = 'Network Error'
    fetchMock.mockRejectedValue(new Error(errorMessage))

    const { result } = renderHook(() => useApiQuery(['tickets'], '/v1/tickets'), {
      wrapper,
    })

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.data).toBeUndefined()
    expect((result.current.error as Error).message).toBe(errorMessage)
  })


  it('deve tratar erro de URL base não configurada', async () => {
    delete process.env.VITE_API_BASE_URL

    const { result } = renderHook(() => useApiQuery(['tickets'], '/v1/tickets'), {
      wrapper,
    })

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect((result.current.error as Error).message).toBe(
      'URL base da API não configurada. Verifique VITE_API_BASE_URL.',
    )

    process.env.VITE_API_BASE_URL = MOCK_API_URL
  })
});
