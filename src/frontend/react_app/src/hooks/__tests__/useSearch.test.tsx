import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useSearch } from '../useSearch'

const originalFetch = global.fetch
global.fetch = jest.fn() as unknown as typeof fetch

afterEach(() => {
  global.fetch = originalFetch
})

let queryClient: QueryClient
const createWrapper = () => {
  queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

test('fetches search results', async () => {
  const wrapper = createWrapper()
  ;(global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: () => Promise.resolve([{ id: 1, name: 'ticket' }]),
  })
  const { result } = renderHook(() => useSearch('ticket'), { wrapper })
  await waitFor(() => expect(result.current.isSuccess).toBe(true))
  expect(result.current.data?.[0].name).toBe('ticket')
})
