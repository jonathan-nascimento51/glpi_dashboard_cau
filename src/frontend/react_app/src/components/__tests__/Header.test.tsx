import { render, screen } from '@testing-library/react'
import Header from '../Header'

describe('Header', () => {
  it('renders brand title', () => {
    render(<Header />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Dashboard')
  })

  it('links search input to results', () => {
    render(<Header />)
    const input = screen.getByPlaceholderText('Buscar...')
    expect(input).toHaveAttribute('aria-controls', 'search-results')
  })
})
