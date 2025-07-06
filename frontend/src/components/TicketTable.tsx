import { VirtualizedTicketTable, TicketRow } from './VirtualizedTicketTable'

interface Props {
  tickets: TicketRow[]
}

export function TicketTable({ tickets }: Props) {
  return (
    <div className="border rounded">
      <div
        className="grid grid-cols-[80px_auto_120px_100px_160px] bg-gray-50 px-2 py-1 text-sm font-semibold"
        role="row"
      >
        <div>ID</div>
        <div>Título</div>
        <div>Status</div>
        <div>Prioridade</div>
        <div>Criado em</div>
      </div>
      <VirtualizedTicketTable rows={tickets} rowHeight={40} />
    </div>
  )
}
