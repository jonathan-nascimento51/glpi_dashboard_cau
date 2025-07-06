import { render, screen } from '@testing-library/react'
import { TicketStatsPage } from '@/features/tickets/TicketStatsPage'

jest.mock('@/features/tickets/api', () => ({
  useTicketMetrics: () => ({
    data: { total: 10, opened: 4, closed: 6 },
    isLoading: false,
    error: null,
  }),
}))

test('renders metrics from the API', () => {
  render(<TicketStatsPage />)
  expect(screen.getAllByTestId('stats-value')[0]).toHaveTextContent('10')
  expect(screen.getAllByTestId('stats-label')[0]).toHaveTextContent('Total')
})