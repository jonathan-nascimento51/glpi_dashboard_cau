import { useMemo } from "react";
import { useTickets } from "../hooks/useTickets";
import { VirtualizedTicketTable } from "./VirtualizedTicketTable";

export default function TicketsDisplay() {
  const { tickets, isLoading, error } = useTickets();

  console.log("tickets recebidos:", tickets);

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

  console.log("tickets filtrados e ordenados:", sortedTickets);

  if (isLoading) return <div>Carregando tickets...</div>;
  if (error) return <div>Erro ao carregar tickets.</div>;
  if (sortedTickets.length === 0) {
    return <div>Nenhum ticket novo encontrado.</div>;
  }

  return <VirtualizedTicketTable rows={sortedTickets} />;
}
