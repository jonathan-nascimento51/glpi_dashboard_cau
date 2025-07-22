import { render, screen } from '@testing-library/react'
import type { Ticket } from '../../types/ticket'
import { TicketTable } from '../../components/TicketTable'

const ticket: Ticket = {
  id: 1,
  name: 'Chamado muito longo com titulo extensivo que precisa ser truncado',
  status: 'New',
  priority: 'High',
  date_creation: new Date('2023-10-27T10:00:00Z'),
}

describe('TicketTable formatting', () => {
  it('formats date and applies styles', () => {
    render(<TicketTable tickets={[ticket]} />)
    const titleCell = screen.getByText(ticket.name)
    expect(titleCell).toHaveAttribute('title', ticket.name)
    expect(screen.getByText('High')).toHaveClass('text-red-600')
    const formatted = new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(ticket.date_creation as Date)
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })

  it('renders placeholders for missing priority and date', () => {
    const missing: Ticket = {
      id: 2,
      name: 'Sem prioridade',
      status: 'New',
      date_creation: null,
    }
    render(<TicketTable tickets={[missing]} />)
    const cells = screen.getAllByRole('cell')
    expect(cells[3]).toHaveTextContent('-')
    expect(cells[4]).toHaveTextContent('-')
  })
})
