import { useMemo } from 'react'
import { useApiQuery } from '../hooks/useApiQuery'
import { EmptyState } from './EmptyState'
import { ErrorMessage } from './ErrorMessage'
import { LoadingSpinner } from './LoadingSpinner'

interface Ticket {
  id: number
  name: string
  status: string
  priority?: string | null
  date_creation?: string | null
}

const formatDate = (value?: string | null) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(value))
  } catch (error) {
    console.error('Error formatting date:', error, 'Input value:', value)
    return '-'
  }
}

export function GlpiTicketsTable() {
  const {
    data: tickets,
    isLoading,
    error,
    isSuccess,
    refetch,
  } = useApiQuery<Ticket[]>(['tickets'], '/tickets')

  const sortedTickets = useMemo(() => {
    if (!tickets) return []
    // Cria uma cópia mutável antes de ordenar
    return [...tickets].sort((a, b) => {
      const dateA = a.date_creation ? new Date(a.date_creation).getTime() : 0
      const dateB = b.date_creation ? new Date(b.date_creation).getTime() : 0
      return dateB - dateA // Ordena pelos mais recentes primeiro
    })
  }, [tickets])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
        <p className="ml-2">Carregando chamados...</p>
      </div>
    )
  }

  if (error) {
    return (
      <ErrorMessage
        title="Erro ao buscar tickets"
        message={error.message || 'Não foi possível carregar os chamados.'}
        onRetry={refetch}
      />
    )
  }

  if (isSuccess && (!sortedTickets || sortedTickets.length === 0)) {
    return (
      <EmptyState
        title="Nenhum chamado encontrado"
        message="Não há chamados para exibir no momento."
        onAction={refetch}
        actionText="Atualizar"
      />
    )
  }

  // Exibe apenas os 3 últimos chamados
  const lastTickets = sortedTickets.slice(0, 3)

  const gridTemplateColumns = 'grid grid-cols-[80px_1fr_120px_100px_160px]';

  return (
    <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800 max-w-3xl mx-auto">
      <h2 className="mb-6 text-2xl font-bold text-gray-800 dark:text-gray-100 text-center tracking-tight">
        Últimos Chamados
      </h2>
      <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
        {/* Cabeçalho da Tabela */}
        <div className={`${gridTemplateColumns} gap-4 bg-gradient-to-r from-blue-50 to-blue-100 px-6 py-3 text-left text-base font-semibold text-blue-900 dark:bg-gray-700 dark:text-blue-200`}>
          <div>ID</div>
          <div>Título</div>
          <div>Status</div>
          <div>Prioridade</div>
          <div>Criado em</div>
        </div>

        {/* Corpo da Tabela - com altura máxima e scroll */}
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {lastTickets.map(ticket => (
            <div
              key={ticket.id}
              className={`${gridTemplateColumns} gap-4 px-6 py-4 text-base text-gray-700 hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-600 transition-colors`}
            >
              <div className="font-semibold text-blue-900 dark:text-white">{ticket.id}</div>
              <div className="truncate" title={ticket.name}>{ticket.name}</div>
              <div>
                <span className="inline-block rounded px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">
                  {ticket.status}
                </span>
              </div>
              <div>
                <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${
                  ticket.priority === 'Alta'
                    ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100'
                    : ticket.priority === 'Média'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                    : ticket.priority === 'Baixa'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-100'
                }`}>
                  {ticket.priority ?? '-'}
                </span>
              </div>
              <div>{formatDate(ticket.date_creation)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
