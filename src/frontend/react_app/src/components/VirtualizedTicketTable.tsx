import {
  memo,
  forwardRef,
  type KeyboardEvent,
  useCallback,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { HTMLAttributes } from 'react';
import { FixedSizeList, type ListChildComponentProps } from 'react-window';
import TicketRow from './TicketRow';

export interface TicketRow {
  id: number | string;
  name: string;
  status?: string;
  requester?: string;
  priority?: string;
  date_creation?: Date | string | null;
  [key: string]: unknown;
}

interface RowData {
  rows: TicketRow[];
  onRowClick: (row: TicketRow) => void;
  onFocus: (index: number) => void;
}

export interface VirtualizedTicketTableProps {
  rows: TicketRow[];
  onRowClick?: (row: TicketRow) => void;
  height?: number;
  rowHeight?: number;
}

const gridTemplateColumns = 'grid grid-cols-[80px_auto_120px_120px_100px_160px]';

const HeaderRow = () => (
  <div
    role="row"
    className={`${gridTemplateColumns} border-b font-bold px-2 py-1 bg-gray-50`}
  >
    <div role="columnheader">ID</div>
    <div role="columnheader">Nome</div>
    <div role="columnheader">Status</div>
    <div role="columnheader">Solicitante</div>
    <div role="columnheader">Prioridade</div>
    <div role="columnheader">Data de Criação</div>
  </div>
);

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
      onClick={handleClick}
      onFocus={handleFocus}
      className="ticket-row" // certifique-se que essa classe está definida no CSS
    >
      <TicketRow ticket={row} />
    </div>
  );
});
Row.displayName = 'Row';

const RowGroup = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  (props, ref) => <div {...props} ref={ref} role="rowgroup" />
);
RowGroup.displayName = 'RowGroup';

export function VirtualizedTicketTable({
  rows,
  onRowClick,
  height = 400,
  rowHeight = 35,
}: VirtualizedTicketTableProps) {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<any>(null);

  const handleRowClick = useCallback(
    (row: TicketRow) => {
      onRowClick?.(row);
    },
    [onRowClick]
  );

  const handleRowFocus = useCallback((index: number) => {
    setFocusedIndex(index);
  }, []);

  const itemData = useMemo(
    () => ({ rows, onRowClick: handleRowClick, onFocus: handleRowFocus }),
    [rows, handleRowClick, handleRowFocus]
  );

  const focusRow = useCallback(
    (index: number) => {
      setFocusedIndex(index);
      listRef.current?.scrollToItem(index);
      const selector = `[data-row-index='${index}']`;
      requestAnimationFrame(() => {
        const el = containerRef.current?.querySelector<HTMLElement>(selector);
        el?.focus();
      });
    },
    []
  );

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>) => {
      const visible = Math.floor(height / rowHeight);
      let newIndex = focusedIndex;

      if (event.key === 'ArrowDown') {
        newIndex = Math.min(focusedIndex + 1, rows.length - 1);
      } else if (event.key === 'ArrowUp') {
        newIndex = Math.max(focusedIndex - 1, 0);
      } else if (event.key === 'PageDown') {
        newIndex = Math.min(focusedIndex + visible, rows.length - 1);
      } else if (event.key === 'PageUp') {
        newIndex = Math.max(focusedIndex - visible, 0);
      } else {
        return;
      }

      event.preventDefault();
      focusRow(newIndex);
    },
    [focusedIndex, rows.length, height, rowHeight, focusRow]
  );

  // Se poucas linhas, renderize sem virtualização
  if (rows.length < 100) {
    return (
      <div
        className="ticket-table divide-y"
        role="table"
        ref={containerRef}
        onKeyDown={handleKeyDown}
      >
        <HeaderRow />
        <div role="rowgroup">
          {rows.map((row, idx) => (
            <div
              key={row.id}
              role="row"
              data-row-index={idx}
              tabIndex={0}
              onClick={() => handleRowClick(row)}
              onFocus={() => handleRowFocus(idx)}
              className="ticket-row"
            >
              <TicketRow ticket={row} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Renderização virtualizada
  return (
    <div className="ticket-table" role="table" ref={containerRef} onKeyDown={handleKeyDown}>
      <HeaderRow />
      {/* @ts-ignore */}
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
  );
}

VirtualizedTicketTable.displayName = 'VirtualizedTicketTable';
