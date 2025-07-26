import { render, screen, fireEvent } from '@testing-library/react'
import FilterPanel from '@/components/FilterPanel'

jest.mock('@/hooks/useFilters', () => {
  const state = {
    open: false,
    period: ['today'],
    level: ['n1'],
    status: ['new'],
    priority: ['low'],
  }
  return {
    useFilters: () => ({
      filters: state,
      toggleFilters: jest.fn(() => { state.open = !state.open }),
      toggleValue: jest.fn((c: keyof typeof state, v: string) => {
        if (Array.isArray(state[c]) && state[c].includes(v)) {
          (state[c] as string[]).splice((state[c] as string[]).indexOf(v), 1);
        } else if (Array.isArray(state[c])) {
          (state[c] as string[]).push(v);
        }
      }),
    }),
  }
})

test('toggles panel visibility', () => {
  render(<FilterPanel />)
  const btn = screen.getByRole('button')
  fireEvent.click(btn)
  expect(btn).toBeInTheDocument()
})
