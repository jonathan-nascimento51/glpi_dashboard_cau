import { useApiQuery } from '../hooks/useApiQuery'

interface Ticket {
  id: number
  name: string
  status: string
  priority?: string | null
  date_creation?: string | null
}

export function GlpiTicketsTable() {
  const {
    data: tickets,
    isLoading,
    error,
    isSuccess,
  } = useApiQuery<Ticket[]>(['tickets'], '/tickets')

  if (isLoading) return <p>Carregando...</p>
  if (error) return <p>Erro ao buscar tickets</p>
  if (isSuccess && (!tickets || tickets.length === 0)) {
    return <p>Nenhum chamado encontrado</p>
  }

  const formatDate = (value?: string | null) => {
    if (!value) return '-'
    try {
      return new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date(value))
    } catch {
      return value
    }
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Título</th>
          <th>Status</th>
          <th>Prioridade</th>
          <th>Criado em</th>
        </tr>
      </thead>
      <tbody>
        {tickets?.map(ticket => (
          <tr key={ticket.id}>
            <td>{ticket.id}</td>
            <td>{ticket.name}</td>
            <td>{ticket.status}</td>
            <td>{ticket.priority ?? '-'}</td>
            <td>{formatDate(ticket.date_creation)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
