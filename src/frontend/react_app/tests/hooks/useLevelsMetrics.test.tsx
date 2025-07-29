import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLevelsMetrics } from '@/hooks/useLevelsMetrics'
import { useApiQuery } from '@/hooks/useApiQuery'

jest.mock('@/hooks/useApiQuery')

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
