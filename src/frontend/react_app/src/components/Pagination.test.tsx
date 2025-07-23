import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from './Pagination'

describe('Pagination component', () => {
  it('renders navigation buttons and pages', () => {
    const onChange = jest.fn()
    render(<Pagination currentPage={2} totalPages={5} onPageChange={onChange} />)

    expect(screen.getByRole('button', { name: /Anterior/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Próxima/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '5' })).toBeInTheDocument()
  })

  it('disables prev and next buttons on edges', () => {
    const onChange = jest.fn()
    const { rerender } = render(
      <Pagination currentPage={1} totalPages={3} onPageChange={onChange} />
    )
    expect(screen.getByLabelText('Página anterior')).toBeDisabled()
    expect(screen.getByLabelText('Próxima página')).not.toBeDisabled()

    rerender(<Pagination currentPage={3} totalPages={3} onPageChange={onChange} />)
    expect(screen.getByLabelText('Próxima página')).toBeDisabled()
  })

  it('calls onPageChange when a button is clicked', () => {
    const onChange = jest.fn()
    render(<Pagination currentPage={1} totalPages={3} onPageChange={onChange} />)

    fireEvent.click(screen.getByRole('button', { name: '2' }))
    expect(onChange).toHaveBeenCalledWith(2)

    fireEvent.click(screen.getByLabelText('Próxima página'))
    expect(onChange).toHaveBeenCalledWith(2)

    fireEvent.click(screen.getByLabelText('Página anterior'))
    expect(onChange).not.toHaveBeenCalledWith(0)
  })
})
