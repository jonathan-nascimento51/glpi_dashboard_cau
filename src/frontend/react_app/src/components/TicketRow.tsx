import { priorityClasses } from './priorityClasses'

export interface TicketRowProps {
  ticket: {
    id: number | string
    name: string
    status?: string
    requester?: string
    priority?: string
    date_creation?: Date | string | null
    [key: string]: unknown
  }
}

export default function TicketRow({ ticket }: TicketRowProps) {
  const formatDate = (value?: string | Date | null) => {
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

  return (
    <div className="grid grid-cols-[80px_auto_120px_120px_100px_160px] ticket-row px-2 py-1 hover:bg-gray-100 cursor-pointer">
      <div role="gridcell">{ticket.id}</div>
      <div role="gridcell" className="truncate" title={ticket.name}>
        {ticket.name}
      </div>
      <div role="gridcell">{ticket.status}</div>
      <div role="gridcell">{ticket.requester ?? '—'}</div>
      <div role="gridcell" className={priorityClasses[ticket.priority ?? '']}>
        {ticket.priority ?? '-'}
      </div>
      <div role="gridcell">{formatDate(ticket.date_creation)}</div>
    </div>
  )
}
