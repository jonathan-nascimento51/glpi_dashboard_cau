import { render, screen } from '@testing-library/react'
import Header from '../Header'

describe('Header', () => {
  it('renders brand title', () => {
    render(<Header />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Centro de Comando')
  })
})
