import { useTickets } from '@/hooks/useTickets'
import { TicketTable } from './TicketTable.js'
import { LoadingSpinner } from './LoadingSpinner.js'
import { ErrorMessage } from './ErrorMessage.js'

export function TicketsDisplay() {
  const { tickets, error, isLoading, refreshTickets } = useTickets()

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

  if (!tickets || tickets.length === 0) {
    return (
      <div className="text-center p-8">
        <h2 className="text-xl font-semibold">Nenhum chamado encontrado</h2>
        <p className="text-gray-500">Não há chamados para exibir no momento.</p>
        <button
          onClick={() => refreshTickets()}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Atualizar
        </button>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard de Chamados GLPI</h1>
      <TicketTable tickets={tickets} />
    </div>
  )
}
