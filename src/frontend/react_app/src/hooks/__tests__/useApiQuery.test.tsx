import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useApiQuery } from '../useApiQuery'

beforeAll(() => {
  process.env.NEXT_PUBLIC_API_BASE_URL = 'http://test-api.com';
});

afterAll(() => {
  delete process.env.NEXT_PUBLIC_API_BASE_URL;
});
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
    expect(result.current.isLoading).toBe(true)
    expect(result.current.error).toBeNull()
  })
})
