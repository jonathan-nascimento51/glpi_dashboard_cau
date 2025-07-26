import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useHotkeys } from '@/hooks/useHotkeys'
import { useFilters } from '@/hooks/useFilters'

jest.mock('@/hooks/useFilters')

const queryClient = new QueryClient()
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

test('Ctrl+F toggles filters', () => {
  const toggleFilters = jest.fn()
  ;(useFilters as jest.Mock).mockReturnValue({ toggleFilters })

  renderHook(() => useHotkeys(), { wrapper })
  window.dispatchEvent(new KeyboardEvent('keydown', { key: 'f', ctrlKey: true }))

  expect(toggleFilters).toHaveBeenCalled()
})

test('Ctrl+R invalidates queries', () => {
  const toggleFilters = jest.fn()
  ;(useFilters as jest.Mock).mockReturnValue({ toggleFilters })
  const invalidate = jest
    .spyOn(queryClient, 'invalidateQueries')
    .mockImplementation(() => Promise.resolve())

  renderHook(() => useHotkeys(), { wrapper })
  window.dispatchEvent(new KeyboardEvent('keydown', { key: 'r', ctrlKey: true }))

  expect(invalidate).toHaveBeenCalled()
})
