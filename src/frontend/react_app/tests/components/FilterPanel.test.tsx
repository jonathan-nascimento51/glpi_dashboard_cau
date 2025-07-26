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
        if (state[c].includes(v)) {
          state[c] = state[c].filter((x: string) => x !== v)
        } else {
          state[c].push(v)
        }
      }),
    }),
  }
})

test('aria-expanded toggles and focus returns to trigger', () => {
  render(<FilterPanel />)
  const btn = screen.getByRole('button')
  expect(btn).toHaveAttribute('aria-expanded', 'false')
  fireEvent.click(btn)
  expect(btn).toHaveAttribute('aria-expanded', 'true')
  fireEvent.click(screen.getByLabelText('Fechar filtros'))
  expect(btn).toHaveAttribute('aria-expanded', 'false')
  expect(document.activeElement).toBe(btn)
})
