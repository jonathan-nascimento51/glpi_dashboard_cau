import { render, screen } from '@testing-library/react'
import type { Ticket } from '../../types/ticket'
import { TicketTable } from '../../components/TicketTable'
import { useApiQuery } from '../../hooks/useApiQuery'

jest.mock('../../hooks/useApiQuery')
const useApiQueryMock = useApiQuery as jest.Mock

const ticket: Ticket = {
  id: 1,
  name: 'Chamado muito longo com titulo extensivo que precisa ser truncado',
  status: 'New',
  priority: 'High',
  date_creation: new Date('2023-10-27T10:00:00Z'),
}

describe('TicketTable formatting', () => {
  beforeEach(() => {
    useApiQueryMock.mockReset()
  })

  it('formats date and applies styles', () => {
    useApiQueryMock.mockReturnValue({ data: { tickets: [ticket] }, isLoading: false, error: null })
    render(<TicketTable />)
    const titleCell = screen.getByText(ticket.name)
    expect(titleCell).toHaveAttribute('title', ticket.name)
    expect(screen.getByText('High')).toHaveClass('text-red-600')
    const formatted = new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(ticket.date_creation as Date)
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })

  it('displays fallbacks when data is missing', () => {
    useApiQueryMock.mockReturnValue({ data: { tickets: [{ id: 99 } as Ticket] }, isLoading: false, error: null })
    render(<TicketTable />)
    const row = screen.getAllByRole('row')[1]
    expect(row).toHaveTextContent('Sem prioridade')
    // priority and date columns should show "-"
    const dashes = row.querySelectorAll('div')
    const dashCount = Array.from(dashes).filter((d) => d.textContent === '-').length
    expect(dashCount).toBeGreaterThanOrEqual(2)
  })
})
