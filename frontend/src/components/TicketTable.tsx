import React from 'react'
import { VirtualizedTicketTable, TicketRow } from './VirtualizedTicketTable'

interface Props {
  tickets: TicketRow[]
}

export function TicketTable({ tickets }: Props) {
  return <VirtualizedTicketTable rows={tickets} />
}
