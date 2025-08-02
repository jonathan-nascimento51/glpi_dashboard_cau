import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useApiQuery } from '../useApiQuery'

const MOCK_API_URL = 'http://test-api.com'
beforeAll(() => {
  process.env.VITE_API_BASE_URL = MOCK_API_URL
})

afterAll(() => {
  delete process.env.VITE_API_BASE_URL
})
beforeEach(() => {
  global.fetch = jest.fn() as unknown as typeof fetch
})

let queryClient: QueryClient
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

beforeEach(() => {
  queryClient = new QueryClient()
})

describe('useApiQuery', () => {
  it('updates state on success', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ foo: 'bar' }),
    })
    const { result } = renderHook(() => useApiQuery(['test'], '/test'), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toEqual({ foo: 'bar' })
    expect(result.current.error).toBeNull()
  })

  it('handles missing base URL', async () => {
    delete process.env.VITE_API_BASE_URL
    ;(global.fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({}) })
    const { result } = renderHook(() => useApiQuery(['t'], '/test'), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect((result.current.error as Error).message).toBe(
      'URL base da API não configurada. Verifique VITE_API_BASE_URL.',
    )
    process.env.VITE_API_BASE_URL = MOCK_API_URL
  })

  it('updates state on error', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValue(new Error('fail'))
    const { result } = renderHook(() => useApiQuery(['test'], '/test'), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeUndefined()
    expect((result.current.error as Error).message).toBe('fail')
  })

  it('updates state on non-ok response', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({ message: 'Not Found' }),
    })
    const { result } = renderHook(() => useApiQuery(['test'], '/test'), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeUndefined()
    expect((result.current.error as Error).message).toContain('Not Found')
  })

  it('ignores abort errors', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValue({ name: 'AbortError' })
    const { result } = renderHook(() => useApiQuery(['test'], '/test'), { wrapper })
    await waitFor(() => expect(global.fetch).toHaveBeenCalled())
    // React Query should ignore abort errors: isError is false, error is null, isLoading is true
    expect(result.current.isLoading).toBe(true)
    expect(result.current.isError).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.status).toBe('loading')
    expect(result.current.data).toBeUndefined()
  })

  it('includes options in query key', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({}) })
    const { result } = renderHook(
      () =>
        useApiQuery(
          ['opts'],
          '/test',
          { staleTime: 1000 },
        ),
      { wrapper },
    )
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    const key = queryClient.getQueryCache().find(['opts', '{"staleTime":1000}'])
    expect(key).toBeDefined()
  })
})
