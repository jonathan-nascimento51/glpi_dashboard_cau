import { renderHook, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { useDashboardData } from '@/hooks/useDashboardData'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map() }}>{children}</SWRConfig>
)

test('loads metrics from API', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    json: () =>
      Promise.resolve({ status: { new: 2, pending: 1, progress: 3, resolved: 4 } }),
  }) as jest.Mock

  const { result } = renderHook(() => useDashboardData(), { wrapper })

  await waitFor(() => expect(result.current.metrics.new).toBe(2))

  expect(result.current.metrics).toEqual({
    new: 2,
    pending: 1,
    progress: 3,
    resolved: 4,
  })
})

test('refreshMetrics triggers refetch', async () => {
  const fetchMock = jest
    .fn()
    .mockResolvedValueOnce({
      status: 200,
      json: () =>
        Promise.resolve({ status: { new: 1, pending: 0, progress: 0, resolved: 0 } }),
    })
    .mockResolvedValueOnce({
      status: 200,
      json: () =>
        Promise.resolve({ status: { new: 5, pending: 4, progress: 3, resolved: 2 } }),
    })
  global.fetch = fetchMock as unknown as typeof fetch

  const { result } = renderHook(() => useDashboardData(), { wrapper })
  await waitFor(() => expect(result.current.metrics.new).toBe(1))

  await result.current.refreshMetrics()
  await waitFor(() => expect(result.current.metrics.new).toBe(5))

  expect(fetchMock).toHaveBeenCalledTimes(2)
})
