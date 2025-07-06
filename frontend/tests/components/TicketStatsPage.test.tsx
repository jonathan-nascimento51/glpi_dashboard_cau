import { render, screen } from '@testing-library/react'
import { TicketStatsPage } from '@/features/tickets/TicketStatsPage'
import * as api from '@/features/tickets/api'

jest.mock('@/features/tickets/api')

const mockedApi = api as jest.Mocked<typeof api>

beforeEach(() => {
  jest.resetAllMocks()
})

test('renders metrics from the API', () => {
  mockedApi.useTicketMetrics.mockReturnValue({
    data: { total: 10, opened: 4, closed: 6 },
    isLoading: false,
    error: null,
  } as any)
  render(<TicketStatsPage />)
  expect(screen.getAllByTestId('stats-value')[0]).toHaveTextContent('10')
  expect(screen.getAllByTestId('stats-label')[0]).toHaveTextContent('Total')
})

test('shows error when fetch fails', () => {
  mockedApi.useTicketMetrics.mockReturnValue({
    data: undefined,
    isLoading: false,
    error: new Error('fail'),
  } as any)
  render(<TicketStatsPage />)
  expect(screen.getByText('Error loading metrics')).toBeInTheDocument()
})
