import React, { useCallback, useMemo, useRef, useState } from 'react'
import { FixedSizeList, ListChildComponentProps } from 'react-window'

export interface TicketRow {
  id: number | string
  name: string
  [key: string]: any
}

interface RowData {
  rows: TicketRow[]
  onRowClick: (row: TicketRow) => void
  onFocus: (index: number) => void
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
  const handleFocus = useCallback(() => data.onFocus(index), [data, index])

  return (
    <div
      style={style}
      role="row"
      data-row-index={index}
      tabIndex={0}
      className="ticket-row border-b px-2 py-1 hover:bg-gray-100 cursor-pointer"
      onClick={handleClick}
      onFocus={handleFocus}
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
  const [focusedIndex, setFocusedIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<FixedSizeList>(null)

  const handleRowClick = useCallback(
    (row: TicketRow) => {
      onRowClick?.(row)
    },
    [onRowClick],
  )

  const handleRowFocus = useCallback((index: number) => {
    setFocusedIndex(index)
  }, [])

  const itemData = useMemo(
    () => ({ rows, onRowClick: handleRowClick, onFocus: handleRowFocus }),
    [rows, handleRowClick, handleRowFocus],
  )

  const focusRow = useCallback(
    (index: number) => {
      setFocusedIndex(index)
      listRef.current?.scrollToItem(index)
      const selector = `[data-row-index='${index}']`
      requestAnimationFrame(() => {
        const el = containerRef.current?.querySelector<HTMLElement>(selector)
        el?.focus()
      })
    },
    [],
  )

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      const visible = Math.floor(height / rowHeight)
      let newIndex = focusedIndex

      if (event.key === 'ArrowDown') {
        newIndex = Math.min(focusedIndex + 1, rows.length - 1)
      } else if (event.key === 'ArrowUp') {
        newIndex = Math.max(focusedIndex - 1, 0)
      } else if (event.key === 'PageDown') {
        newIndex = Math.min(focusedIndex + visible, rows.length - 1)
      } else if (event.key === 'PageUp') {
        newIndex = Math.max(focusedIndex - visible, 0)
      } else {
        return
      }

      event.preventDefault()
      focusRow(newIndex)
    },
    [focusedIndex, rows.length, height, rowHeight, focusRow],
  )

  if (rows.length < 100) {
    return (
      <div
        className="ticket-table divide-y"
        role="table"
        ref={containerRef}
        onKeyDown={handleKeyDown}
      >
        <div role="rowgroup">
          {rows.map((row, idx) => (
            <div
              key={row.id}
              role="row"
              data-row-index={idx}
              tabIndex={0}
              className="ticket-row px-2 py-1 hover:bg-gray-100 cursor-pointer"
              style={{ height: rowHeight }}
              onClick={() => handleRowClick(row)}
              onFocus={() => handleRowFocus(idx)}
            >
              {row.name}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div
      role="table"
      ref={containerRef}
      onKeyDown={handleKeyDown}
    >
      <FixedSizeList
        ref={listRef}
        height={height}
        itemCount={rows.length}
        itemSize={rowHeight}
        width="100%"
        itemData={itemData}
        outerElementType={React.forwardRef<HTMLDivElement>((props, ref) => (
          <div {...props} ref={ref} role="rowgroup" />
        ))}
      >
        {Row}
      </FixedSizeList>
    </div>
  )
}
