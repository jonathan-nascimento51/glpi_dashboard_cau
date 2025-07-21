import { VirtualizedTicketTable, type TicketRow } from './VirtualizedTicketTable'
import type { Ticket } from '../types/ticket'

interface Props {
  readonly tickets: Ticket[]
}

export function TicketTable({ tickets }: Props) {
  return (
    <div className="border rounded" aria-label="Lista de chamados">
      <table className="w-full border-separate border-spacing-0">
        <thead>
          <tr className="grid grid-cols-[80px_auto_120px_100px_160px] bg-gray-50 px-2 py-1 text-sm font-semibold">
            <th scope="col">ID</th>
            <th scope="col">Título</th>
            <th scope="col">Status</th>
            <th scope="col">Prioridade</th>
            <th scope="col">Criado em</th>
          </tr>
        </thead>
        {/* The VirtualizedTicketTable should render <tbody> rows if possible */}
      </table>
      <VirtualizedTicketTable rows={tickets as TicketRow[]} rowHeight={40} />
    </div>
  )
}
