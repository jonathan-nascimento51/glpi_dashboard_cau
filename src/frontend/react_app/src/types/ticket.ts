import type { Urgency, Impact, TicketType } from './api'

export interface Ticket {
  id: number | string
  name: string
  status?: string
  requester?: string
  group?: string
  priority?: string
  urgency?: Urgency
  impact?: Impact
  type?: TicketType
  date_creation?: Date | null
  assigned_to?: string
  solvedate?: string | null
  closedate?: string | null
  content?: string | null
}
