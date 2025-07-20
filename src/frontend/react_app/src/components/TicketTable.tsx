import { VirtualizedTicketTable, type TicketRow } from './VirtualizedTicketTable'

interface Props {
  tickets: TicketRow[]
}

export function TicketTable({ tickets }: Props) {
  return (
    <div className="border rounded" aria-label="Lista de chamados">
      <div role="rowgroup">
        <div
          className="grid grid-cols-[80px_auto_120px_100px_160px] bg-gray-50 px-2 py-1 text-sm font-semibold"
          role="row"
        >
          <div role="columnheader">ID</div>
          <div role="columnheader">Título</div>
          <div role="columnheader">Status</div>
          <div role="columnheader">Prioridade</div>
          <div role="columnheader">Criado em</div>
        </div>
      </div>
      <VirtualizedTicketTable rows={tickets} rowHeight={40} />
    </div>
  )
}
