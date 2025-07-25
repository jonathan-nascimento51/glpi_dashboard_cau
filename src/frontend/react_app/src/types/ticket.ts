import type { Urgency, Impact, TicketType } from './api'

export interface Ticket {
  id: number | string
  name: string
  content?: string | null
  status?: string
  priority?: string
  urgency?: Urgency
  impact?: Impact
  type?: TicketType
  date_creation?: Date | null
  requester?: string
  assigned_to?: string
  solvedate?: string | null
  closedate?: string | null
}
