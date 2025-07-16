import { renderHook, act } from '@testing-library/react'
import { useFilters } from '@/hooks/useFilters'

test('toggles filter panel', () => {
  const { result } = renderHook(() => useFilters())
  act(() => result.current.toggleFilters())
  expect(result.current.filters.open).toBe(true)
})

test('toggleValue adds and removes entries', () => {
  const { result } = renderHook(() => useFilters())
  act(() => result.current.toggleValue('status', 'closed'))
  expect(result.current.filters.status).toContain('closed')
  act(() => result.current.toggleValue('status', 'closed'))
  expect(result.current.filters.status).not.toContain('closed')
})
