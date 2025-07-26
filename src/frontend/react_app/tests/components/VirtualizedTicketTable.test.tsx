import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { VirtualizedTicketTable } from '@/components/VirtualizedTicketTable'
import { jest } from '@jest/globals'

// Cria um mock para o react-window, sobrescrevendo o FixedSizeList
jest.mock('react-window', () => ({
  FixedSizeList: jest.fn(function FixedSizeList(props: {
    itemCount: number
    itemData?: any
    children: (args: { index: number; style: React.CSSProperties }) => JSX.Element
  }) {
    return (
      <div data-testid="virtual-list">
        {Array.from({ length: props.itemCount }).map((_, idx) => (
          <div key={idx} role="row" tabIndex={0}>
            {props.children({ index: idx, style: {} })}
          </div>
        ))}
      </div>
    )
  }),
}))

// Importa o FixedSizeList do módulo mockado
import { FixedSizeList } from 'react-window'

const buildRows = (count: number) =>
  Array.from({ length: count }, (_, i) => ({ id: i, name: `Row ${i}` }))

const getRow = (index: number) => screen.getByText(`Row ${index}`)

describe('VirtualizedTicketTable', () => {
  beforeEach(() => {
    ;(FixedSizeList as jest.Mock).mockClear()
  })

  test('uses FixedSizeList when rows >= 100', () => {
    render(<VirtualizedTicketTable rows={buildRows(120)} />)
    expect(FixedSizeList).toHaveBeenCalled()
    expect(screen.getByRole('table')).not.toHaveClass('ticket-table')
  })

  test('renders plain rows below threshold', () => {
    render(<VirtualizedTicketTable rows={buildRows(50)} />)
    expect(FixedSizeList).not.toHaveBeenCalled()
    expect(screen.getByRole('table')).toHaveClass('ticket-table')
  })

  test('keyboard navigation works in virtualized list', async () => {
    render(<VirtualizedTicketTable rows={buildRows(120)} />)
    const table = screen.getByRole('table')
    const first = getRow(0)
    const second = getRow(1)
    const eleventh = getRow(11)

    first.focus()
    fireEvent.keyDown(table, { key: 'ArrowDown' })
    await waitFor(() => expect(document.activeElement).toBe(second))
    fireEvent.keyDown(table, { key: 'ArrowUp' })
    await waitFor(() => expect(document.activeElement).toBe(first))
    fireEvent.keyDown(table, { key: 'PageDown' })
    await waitFor(() => expect(document.activeElement).toBe(eleventh))
    fireEvent.keyDown(table, { key: 'PageUp' })
    await waitFor(() => expect(document.activeElement).toBe(first))
  })

  test('keyboard navigation works in plain list', async () => {
    render(<VirtualizedTicketTable rows={buildRows(20)} />)
    // Removed unused declaration for table since it's not needed.
    const first = getRow(0)
    const second = getRow(1)

    first.focus()
    // Dispara o evento de keyDown diretamente no elemento focalizado
    fireEvent.keyDown(first, { key: 'ArrowDown' })
    await waitFor(() => expect(document.activeElement).toBe(second))
    fireEvent.keyDown(second, { key: 'ArrowUp' })
    await waitFor(() => expect(document.activeElement).toBe(first))
  })
})
