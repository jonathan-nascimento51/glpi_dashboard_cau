import React, { useCallback, useMemo } from 'react'
import { FixedSizeList, ListChildComponentProps } from 'react-window'

export interface TicketRow {
  id: number | string
  name: string
  [key: string]: any
}

interface RowData {
  rows: TicketRow[]
  onRowClick: (row: TicketRow) => void
}

export interface VirtualizedTicketTableProps {
  rows: TicketRow[]
  onRowClick?: (row: TicketRow) => void
  height?: number
  rowHeight?: number
}

const Row = React.memo(({ index, style, data }: ListChildComponentProps<RowData>) => {
  const row = data.rows[index]
  const handleClick = useCallback(() => data.onRowClick(row), [data, row])

  return (
    <div
      style={style}
      className="ticket-row border-b px-2 py-1 hover:bg-gray-100 cursor-pointer"
      onClick={handleClick}
    >
      {row.name}
    </div>
  )
})
Row.displayName = 'Row'

export function VirtualizedTicketTable({
  rows,
  onRowClick,
  height = 400,
  rowHeight = 35,
}: VirtualizedTicketTableProps) {
  const handleRowClick = useCallback(
    (row: TicketRow) => {
      onRowClick?.(row)
    },
    [onRowClick],
  )

  const itemData = useMemo(
    () => ({ rows, onRowClick: handleRowClick }),
    [rows, handleRowClick],
  )

  if (rows.length < 100) {
    return (
      <div className="ticket-table divide-y">
        {rows.map((row) => (
          <div
            key={row.id}
            className="ticket-row px-2 py-1 hover:bg-gray-100 cursor-pointer"
            style={{ height: rowHeight }}
            onClick={() => handleRowClick(row)}
          >
            {row.name}
          </div>
        ))}
      </div>
    )
  }

  return (
    <FixedSizeList
      height={height}
      itemCount={rows.length}
      itemSize={rowHeight}
      width="100%"
      itemData={itemData}
    >
      {Row}
    </FixedSizeList>
  )
}
