import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useTickets } from '@/hooks/useTickets'
import { DEFAULT_FILTERS } from '@/hooks/useFilters'

const queryClient = new QueryClient()
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

test('fetches tickets from API', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    json: () => Promise.resolve([{ id: 1, name: 't1', group: 'N1' }]),
  }) as jest.Mock

  const { result } = renderHook(() => useTickets(DEFAULT_FILTERS), { wrapper })
  expect(result.current.isLoading).toBe(true)
  await waitFor(() => expect(result.current.isLoading).toBe(false))
  expect(result.current.isSuccess).toBe(true)
  expect(result.current.tickets).toHaveLength(1)
  expect(result.current.tickets?.[0].name).toBe('t1')
  expect(result.current.tickets?.[0].group).toBe('N1')
})

test('handles API error', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 500,
    text: () => Promise.resolve('fail'),
  }) as jest.Mock

  const { result } = renderHook(() => useTickets(DEFAULT_FILTERS), { wrapper })
  await waitFor(() => expect(result.current.error).toBeTruthy())
  expect(result.current.isSuccess).toBe(false)
})

test('applies filters to query', async () => {
  const fetchMock = jest.fn().mockResolvedValue({
    status: 200,
    json: () => Promise.resolve([]),
  })
  global.fetch = fetchMock as unknown as typeof fetch

  renderHook(() => useTickets(DEFAULT_FILTERS), { wrapper })
  await waitFor(() => expect(fetchMock).toHaveBeenCalled())
  expect(fetchMock.mock.calls[0][0]).toContain('tickets?')
})
