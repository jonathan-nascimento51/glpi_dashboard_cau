import {
  memo,
  forwardRef,
  type KeyboardEvent,
  useCallback,
  useMemo,
  useRef,
  useState,
} from 'react'
import type { ReactNode, HTMLAttributes } from 'react'
import { type ListChildComponentProps } from 'react-window'

const priorityClasses: Record<string, string> = {
  'Very High': 'text-red-700',
  High: 'text-red-600',
  Major: 'text-red-800',
  Medium: 'text-yellow-600',
  Low: 'text-green-600',
  'Very Low': 'text-green-700',
}

const formatDate = (value?: string | Date | null) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(value))
  } catch (error) {
    console.error('Error formatting date:', error, 'Input value:', value)
    return '-'
  }
}

export interface TicketRow {
  id: number | string
  name: string
  status?: string
  requester?: string
  priority?: string
  date_creation?: Date | string | null
  [key: string]: unknown
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
  rowHeightClass?: string
}

const gridTemplateColumns = 'grid grid-cols-[80px_auto_120px_120px_100px_160px]';

const Row = memo(({ index, style, data }: ListChildComponentProps<RowData>) => {
  const row = data.rows[index];
  const handleClick = useCallback(() => data.onRowClick(row), [data, row]);
  const handleFocus = useCallback(() => data.onFocus(index), [data, index]);

  return (
    <div
      style={style}
      role="row"
      data-row-index={index}
      tabIndex={0}
      className={`${gridTemplateColumns} ticket-row border-b px-2 py-1 hover:bg-gray-100 cursor-pointer`}
      onClick={handleClick}
      onFocus={handleFocus}
    >
      <div role="cell">{row.id}</div>
      <div role="cell" className="truncate" title={row.name}>{row.name}</div>
      <div role="cell">{row.status}</div>
      <div role="cell">{row.requester ?? '—'}</div>
      <div role="cell" className={priorityClasses[row.priority ?? '']}>
        {row.priority ?? '-'}
      </div>
      <div role="cell">{formatDate(row.date_creation) as ReactNode}</div>
    </div>
  );
})
Row.displayName = 'Row'

const RowGroup = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  (props, ref) => <div {...props} ref={ref} role="rowgroup" />,
)
RowGroup.displayName = 'RowGroup'

export function VirtualizedTicketTable({
  rows,
  onRowClick,
  height = 400,
  rowHeight = 35,
  rowHeightClass = 'h-[35px]',
}: VirtualizedTicketTableProps) {
  const [focusedIndex, setFocusedIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<any>(null)

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
    (event: KeyboardEvent<HTMLDivElement>) => {
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

// Fix the FixedSizeList mock so that props.children is called as a function if it is one, otherwise render it directly.
const FixedSizeList = (props: any) => (
  <div>
    {Array.from({ length: props.itemCount }).map((_, idx) => (
      <div key={idx} role="row" tabIndex={0}>
        {typeof props.children === "function"
          ? props.children({ index: idx, style: {}, data: props.itemData })
          : props.children}
      </div>
    ))}
  </div>
);

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
              className={`grid grid-cols-[80px_auto_120px_120px_100px_160px] ticket-row px-2 py-1 hover:bg-gray-100 cursor-pointer ${rowHeightClass}`}
              onClick={() => handleRowClick(row)}
              onFocus={() => handleRowFocus(idx)}
            >
              <div role="cell">{row.id}</div>
              <div role="cell" className="truncate" title={row.name}>{row.name}</div>
              <div role="cell">{row.status}</div>
              <div role="cell">{row.requester ?? '—'}</div>
              <div role="cell" className={priorityClasses[row.priority ?? '']}>
                {row.priority ?? '-'}
              </div>
              <div role="cell">{formatDate(row.date_creation) as ReactNode}</div>
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
      {/* @ts-ignore `FixedSizeList` props are untyped in our stub */}
      <FixedSizeList
        ref={listRef}
        height={height}
        itemCount={rows.length}
        itemSize={rowHeight}
        width="100%"
        itemData={itemData}
        innerElementType={RowGroup}
      >
        {Row}
      </FixedSizeList>
    </div>
  )
}

VirtualizedTicketTable.displayName = 'VirtualizedTicketTable'
