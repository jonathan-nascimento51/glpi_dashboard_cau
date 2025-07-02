import React from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './app/queryClient'
import { TicketStatsPage } from './features/tickets/TicketStatsPage'
import './App.css'

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Ticket Statistics</h1>
        <TicketStatsPage />
      </div>
    </QueryClientProvider>
  )
}
