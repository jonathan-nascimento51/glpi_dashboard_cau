import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useMetricsLevels } from '../useMetricsLevels'
import { useApiQuery } from '../useApiQuery'

jest.mock('../useApiQuery')

const createWrapper = () => {
  const queryClient = new QueryClient()
  return {
    queryClient,
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    ),
  }
}

test('maps and sorts API record to levels array', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({
    data: {
      N2: { new: 2, progress: 1, pending: 0, resolved: 3 },
      N1: { new: 1, progress: 2, pending: 3, resolved: 4 },
    },
    isLoading: false,
    isError: false,
    error: null,
  })
  const { wrapper } = createWrapper()
  const { result } = renderHook(() => useMetricsLevels(), { wrapper })
  expect(result.current.levels).toEqual([
    { name: 'N1', metrics: { new: 1, progress: 2, pending: 3, resolved: 4 } },
    { name: 'N2', metrics: { new: 2, progress: 1, pending: 0, resolved: 3 } },
  ])
})

test('refresh calls query.refetch', () => {
  const refetch = jest.fn()
  ;(useApiQuery as jest.Mock).mockReturnValue({ data: {}, isLoading: false, refetch })
  const { wrapper } = createWrapper()
  const { result } = renderHook(() => useMetricsLevels(), { wrapper })
  result.current.refresh()
  expect(refetch).toHaveBeenCalled()
})
