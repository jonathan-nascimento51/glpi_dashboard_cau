import { render, screen } from '@testing-library/react'
import type { Ticket } from '../../types/ticket'
import { TicketTable } from '../../components/TicketTable'

const ticket: Ticket = {
  id: 1,
  name: 'Chamado muito longo com titulo extensivo que precisa ser truncado',
  status: 'New',
  priority: 'High',
  requester: 'Alice',
  date_creation: new Date('2023-10-27T10:00:00Z'),
}

describe('TicketTable formatting', () => {
  it('formats date and applies styles', () => {
    render(<TicketTable tickets={[ticket]} />)
    const titleCell = screen.getByText(ticket.name)
    expect(titleCell).toHaveAttribute('title', ticket.name)
    expect(screen.getByText('High')).toHaveClass('text-red-600')
    expect(screen.getByText('Alice')).toBeInTheDocument()
    const formatted = new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(ticket.date_creation as Date)
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })

  it('displays fallbacks when data is missing', () => {
    render(<TicketTable tickets={[{ id: 99 } as Ticket]} />)
    const row = screen.getAllByRole('row')[1]
    // requester, priority and date columns should show the fallback "—" or "-"
    const cells = row.querySelectorAll('div')
    const fallbackCount = Array.from(cells).filter((d) => d.textContent === '—' || d.textContent === '-').length
    // Number of columns (requester, priority, date) expected to show fallback values when data is missing
    const FALLBACK_COLUMN_COUNT = 3
    expect(fallbackCount).toBeGreaterThanOrEqual(FALLBACK_COLUMN_COUNT)
  })
})
