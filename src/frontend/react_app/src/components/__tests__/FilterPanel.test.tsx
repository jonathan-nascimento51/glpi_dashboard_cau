import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import FilterPanel from '../FilterPanel'

expect.extend(toHaveNoViolations)

describe('FilterPanel', () => {
  test('focus moves to close button when opened and returns on close', async () => {
    render(<FilterPanel />)
    const toggle = screen.getByRole('button', { name: /Abrir filtros/i })
    fireEvent.click(toggle)
    const close = screen.getByRole('button', { name: /Fechar filtros/i })
    await waitFor(() => expect(close).toBe(document.activeElement))
    fireEvent.click(close)
    await waitFor(() => expect(toggle).toBe(document.activeElement))
  })

  test('toggling options updates filter state', async () => {
    render(<FilterPanel />)
    fireEvent.click(screen.getByRole('button', { name: /Abrir filtros/i }))
    const option = screen.getByTestId('filter-today')
    expect(option.querySelector('[data-testid="filter-checkbox"]')).toHaveClass('checked')
    fireEvent.click(option)
    await waitFor(() =>
      expect(screen.queryByText('today')).not.toBeInTheDocument(),
    )
  })

  test('axe accessibility check', async () => {
    const { container } = render(<FilterPanel />)
    const results = await axe(container, { rules: { 'aria-dialog-name': { enabled: false } } })
    expect(results).toHaveNoViolations()
  })
})
