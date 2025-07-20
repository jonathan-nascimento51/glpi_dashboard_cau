import React from 'react'
import { render, screen } from '@testing-library/react'
import type { TicketRow } from '../../components/VirtualizedTicketTable'
import { TicketTable } from '../../components/TicketTable'

const ticket: TicketRow = {
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
    }).format(ticket.date_creation!)
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })
})
