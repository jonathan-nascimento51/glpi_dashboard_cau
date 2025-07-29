import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'
import { useMetricsOverview } from '../../hooks/useMetricsOverview'

jest.mock('../../hooks/useMetricsOverview')
const mockedHook = useMetricsOverview as jest.Mock

const mockMetrics = {
  N1: { open: 5, closed: 2 },
  N2: { open: 1, closed: 3 },
}

function setup() {
  return render(<Dashboard />)
}

describe('Dashboard component', () => {
  beforeEach(() => {
    mockedHook.mockReset()
  })

  it('shows loading indicator initially', () => {
    mockedHook.mockReturnValue({
      metrics: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refreshMetrics: jest.fn(),
    })
    setup()
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders metric cards after fetch', () => {
    mockedHook.mockReturnValue({
      metrics: mockMetrics,
      isLoading: false,
      isError: false,
      error: null,
      refreshMetrics: jest.fn(),
    })
    setup()
    expect(screen.getByTestId('card-N1')).toBeInTheDocument()
    expect(screen.getByText('Abertos: 5')).toBeInTheDocument()
    expect(screen.getByText('Fechados: 2')).toBeInTheDocument()
    const cards = screen.getAllByTestId(/card-/)
    expect(cards).toHaveLength(Object.keys(mockMetrics).length)
  })

  it('shows error message on failure', () => {
    mockedHook.mockReturnValue({
      metrics: undefined,
      isLoading: false,
      isError: true,
      error: new Error('fail'),
      refreshMetrics: jest.fn(),
    })
    setup()
    expect(screen.getByText(/Não foi possível carregar/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument()
  })

  it('retries fetch when retry button is clicked', () => {
    const refresh = jest.fn()
    mockedHook.mockReturnValue({
      metrics: undefined,
      isLoading: false,
      isError: true,
      error: new Error('fail'),
      refreshMetrics: refresh,
    })
    setup()
    screen.getByRole('button', { name: /tentar novamente/i }).click()
    expect(refresh).toHaveBeenCalled()
  })
})
