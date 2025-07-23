import { useState, useMemo, useEffect } from 'react'
import { useTickets } from '../hooks/useTickets'
import { TicketTable } from './TicketTable'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'
import { EmptyState } from './EmptyState'
import Pagination from './Pagination'

const ITEMS_PER_PAGE = 15;

function TicketsDisplay() {
  const { tickets, error, isLoading, isSuccess, refreshTickets } = useTickets()
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    setCurrentPage(1)
  }, [tickets])

  const paginatedTickets = useMemo(
    () => tickets?.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE) ?? [],
    [tickets, currentPage]
  )
  const totalPages = tickets ? Math.ceil(tickets.length / ITEMS_PER_PAGE) : 1

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <ErrorMessage
        title="Erro ao carregar os chamados"
        message={error.message || 'Não foi possível conectar à API. Tente novamente mais tarde.'}
        onRetry={refreshTickets}
      />
    )
  }

  if (isSuccess && (!tickets || tickets.length === 0)) {
    return <EmptyState
      title="Nenhum chamado encontrado"
      message="Não há chamados para exibir no momento."
      onAction={refreshTickets}
      actionText="Atualizar"
    />
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard de Chamados GLPI</h1>
      <TicketTable tickets={paginatedTickets} />
      {totalPages > 1 && (
        <Pagination
          className="mt-4"
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      )}
    </div>
  )
}

export default TicketsDisplay
