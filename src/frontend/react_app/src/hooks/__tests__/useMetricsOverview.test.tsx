import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useMetricsOverview } from '../useMetricsOverview'
import { useApiQuery } from '../useApiQuery'

jest.mock('../useApiQuery')

test('calls aggregated metrics endpoint', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({
    data: { open_tickets: {}, tickets_closed_this_month: {} },
    isLoading: false,
    isError: false,
    error: null,
  })
  const { wrapper } = createWrapper()
  renderHook(() => useMetricsOverview(), { wrapper })
  expect(useApiQuery).toHaveBeenCalledWith(
    ['metrics-overview'],
    '/v1/metrics/aggregated',
    expect.any(Object),
  )
})

const createWrapper = () => {
  const queryClient = new QueryClient()
  return {
    queryClient,
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    ),
  }
}

test('builds metrics from API data', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({
    data: {
      open_tickets: { N1: 5, N2: 2 },
      tickets_closed_this_month: { N1: 1, N2: 0 },
    },
    isLoading: false,
    isError: false,
    error: null,
  })
  const { wrapper } = createWrapper()
  const { result } = renderHook(() => useMetricsOverview(), { wrapper })
  expect(result.current.metrics).toEqual({
    N1: { open: 5, closed: 1 },
    N2: { open: 2, closed: 0 },
  })
})

test('refreshMetrics invalidates query', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({
    data: { open_tickets: {}, tickets_closed_this_month: {} },
    isLoading: false,
  })
  const { queryClient, wrapper } = createWrapper()
  const invalidate = jest.spyOn(queryClient, 'invalidateQueries')
  const { result } = renderHook(() => useMetricsOverview(), { wrapper })
  result.current.refreshMetrics()
  expect(invalidate).toHaveBeenCalledWith({ queryKey: ['metrics-overview'] })
})
