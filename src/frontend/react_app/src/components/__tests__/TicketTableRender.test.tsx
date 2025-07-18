import { render, screen } from '@testing-library/react'
import { TicketTable } from '@/components/TicketTable.js'
import type { TicketRow } from '@/components/VirtualizedTicketTable.js'
import React from 'react'

jest.mock('react-window', () => {
  return {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    FixedSizeList: jest.fn((props: any) => (
      <div data-testid="virtual-list">
        {Array.from({ length: props.itemCount }).map((_: any, idx: number) =>
          React.createElement(props.children, {
            index: idx,
            style: {},
            data: props.itemData,
          })
        )}
      </div>
    )),
  }
}, { virtual: true })

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
