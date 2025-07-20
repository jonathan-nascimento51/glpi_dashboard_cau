import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface Ticket {
  id: number
  name: string
  status: string
}

export function GlpiTicketsTable() {
  const { data: tickets, isLoading, error } = useQuery<Ticket[]>({
    queryKey: ['tickets'],
    queryFn: async () => {
      const { data } = await axios.get<Ticket[]>('/api/tickets')
      return data
    },
  })

  if (isLoading) return <p>Carregando...</p>
  if (error) return <p>Erro ao buscar tickets</p>

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Título</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {tickets?.map(ticket => (
          <tr key={ticket.id}>
            <td>{ticket.id}</td>
            <td>{ticket.name}</td>
            <td>{ticket.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
