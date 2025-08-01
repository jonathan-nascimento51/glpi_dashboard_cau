import { useMemo } from "react";
import { useTickets } from "../hooks/useTickets";
import { VirtualizedTicketTable } from "./VirtualizedTicketTable";

export default function TicketsDisplay() {
  const { tickets, isLoading, error } = useTickets();

  // Filtra somente os tickets com status "novo" (insensível a maiúsculas/minúsculas)
  const filteredTickets = useMemo(() => {
    if (!tickets) return [];
    return tickets.filter(
      (ticket) => String(ticket.status).toLowerCase().trim() === "new"
    );
  }, [tickets]);

  // Ordena do mais recente para o mais antigo
  const sortedTickets = useMemo(() => {
    return [...filteredTickets].sort(
      (a, b) =>
        new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime()
    );
  }, [filteredTickets]);

  if (isLoading)
    return (
      <div className="flex items-center justify-center p-6 bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg min-h-[180px]">
        <span className="text-base text-muted">Carregando tickets...</span>
      </div>
    );
  if (error)
    return (
      <div className="flex items-center justify-center p-6 bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg min-h-[180px]">
        <span className="text-base text-red-500">Erro ao carregar tickets.</span>
      </div>
    );
  if (sortedTickets.length === 0) {
    return (
      <div className="flex items-center justify-center p-6 bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg min-h-[180px]">
        <span className="text-base text-muted">Nenhum ticket novo encontrado.</span>
      </div>
    );
  }

  return (
    <div className="bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg p-6 flex flex-col gap-4">
      <div className="flex flex-row items-center justify-between px-2 pb-3 border-b border-border/60 min-h-[48px]">
        <div className="levels-title">Tickets Novos</div>
        <div className="levels-subtitle">Entradas Recentes</div>
      </div>
      <VirtualizedTicketTable rows={sortedTickets} />
    </div>
  );
}
