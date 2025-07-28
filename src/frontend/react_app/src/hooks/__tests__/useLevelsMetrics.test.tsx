import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLevelsMetrics } from '../useLevelsMetrics'
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

test('maps API record to levels array', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({
    data: { N1: { new: 1, progress: 2, pending: 3, resolved: 4 } },
    isLoading: false,
    isError: false,
    error: null,
  })
  const { wrapper } = createWrapper()
  const { result } = renderHook(() => useLevelsMetrics(), { wrapper })
  expect(result.current.levels).toEqual([
    { name: 'N1', metrics: { new: 1, progress: 2, pending: 3, resolved: 4 } },
  ])
})

test('refreshLevels invalidates query', () => {
  ;(useApiQuery as jest.Mock).mockReturnValue({ data: {}, isLoading: false })
  const { queryClient, wrapper } = createWrapper()
  const invalidate = jest.spyOn(queryClient, 'invalidateQueries')
  const { result } = renderHook(() => useLevelsMetrics(), { wrapper })
  result.current.refreshLevels()
  expect(invalidate).toHaveBeenCalledWith({ queryKey: ['levels-metrics'] })
})
