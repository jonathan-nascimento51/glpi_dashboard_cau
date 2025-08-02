import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useTicketMetrics } from '../api'
import { useApiQuery } from '../../../hooks/useApiQuery'

jest.mock('../../../hooks/useApiQuery')

const createWrapper = () => {
  const queryClient = new QueryClient()
  return {
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
  }
}

test('validates response structure with select', () => {
  const valid = { status: { open: 1 }, per_user: { alice: 2 } }
  let opts: any
  ;(useApiQuery as jest.Mock).mockImplementation(
    (_key: unknown, _endpoint: string, options: any) => {
      opts = options
      return { data: valid, isLoading: false, isError: false, error: null }
    }
  )
  const { wrapper } = createWrapper()
  const { result } = renderHook(() => useTicketMetrics(), { wrapper })
  expect(result.current.data).toEqual(valid)
  const select = opts.select as (data: unknown) => unknown
  expect(select(valid)).toEqual(valid)
  expect(() => select({ status: { open: 'x' }, per_user: {} })).toThrow(
    'Invalid response structure for MetricsOverview'
  )
  expect(() => select({ status: {}, per_user: 'y' })).toThrow(
    'Invalid response structure for MetricsOverview'
  )
  expect(() => select({})).toThrow(
    'Invalid response structure for MetricsOverview'
  )
})
