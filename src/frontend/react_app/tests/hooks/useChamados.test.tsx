import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useChamadosPorData } from '@/hooks/useChamadosPorData'
import { useChamadosPorDia } from '@/hooks/useChamadosPorDia'

const queryClient = new QueryClient()
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

beforeEach(() => {
  jest.resetAllMocks()
})

test('useChamadosPorData parses numbers', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    json: () => Promise.resolve([{ date: '2024-01-01', total: '2' }]),
  }) as jest.Mock

  const { result } = renderHook(() => useChamadosPorData(), { wrapper })
  expect(result.current.isLoading).toBe(true)
  await waitFor(() => expect(result.current.isLoading).toBe(false))
  expect(result.current.dados).toEqual([{ date: '2024-01-01', total: 2 }])
})

test('useChamadosPorData handles error', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 500,
    text: () => Promise.resolve('fail'),
  }) as jest.Mock

  const { result } = renderHook(() => useChamadosPorData(), { wrapper })
  await waitFor(() => expect(result.current.error).toBeTruthy())
})

test('useChamadosPorDia handles error', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 500,
    text: () => Promise.resolve('fail'),
  }) as jest.Mock

  const { result } = renderHook(() => useChamadosPorDia(), { wrapper })
  await waitFor(() => expect(result.current.error).toBeTruthy())
})
