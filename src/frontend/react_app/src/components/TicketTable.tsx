import { useApiQuery } from '../hooks/useApiQuery'
import { VirtualizedTicketTable, type TicketRow } from './VirtualizedTicketTable';
import type { Ticket } from '../types/ticket';

// A interface para a resposta esperada da API.
// A API pode retornar um objeto com uma chave 'tickets'.
interface TicketsApiResponse {
  tickets: Ticket[];
}

export function TicketTable() {
  const { data, isLoading, error } = useApiQuery<TicketsApiResponse>(
    ['tickets'],
    '/tickets',
  );

  if (isLoading) {
    return <div className="p-4 text-center">Carregando chamados...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Erro ao carregar dados: {error}</div>;
  }

  const tickets = data?.tickets ?? [];

  if (tickets.length === 0) {
    return <div className="p-4 text-center">Nenhum chamado encontrado.</div>;
  }

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
      <VirtualizedTicketTable rows={tickets.map(mapTicketToTicketRow)} rowHeight={40} />
    </div>
  );
}

function mapTicketToTicketRow(ticket: Ticket): TicketRow {
  return {
    id: ticket.id,
    name: ticket.name,
    status: ticket.status,
    priority: ticket.priority,
    // Use `undefined` when the date is missing so the formatter displays a fallback
    date_creation:
      ticket.date_creation != null ? new Date(ticket.date_creation) : undefined,
  };
}
