import { useTickets } from '../hooks/useTickets'
import { TicketTable } from './TicketTable'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'
import { EmptyState } from './EmptyState'

function TicketsDisplay() {
  const { tickets, error, isLoading, isSuccess, refreshTickets } = useTickets()

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
      <TicketTable tickets={tickets} />
    </div>
  )
}

export default TicketsDisplay
