import { render, screen } from '@testing-library/react'
import { LevelsPanel } from '@/components/LevelsPanel'
import { useMetricsOverview } from '@/hooks/useMetricsOverview'
import { ErrorMessage } from '@/components/ErrorMessage'
import { EmptyState } from '@/components/EmptyState'

jest.mock('@/hooks/useMetricsOverview')
const mockedHook = useMetricsOverview as jest.Mock

function LevelsPanelWrapper() {
  const { metrics, isLoading, isError, error } = useMetricsOverview()

  if (isLoading) {
    return <div data-testid="skeleton" className="skeleton" />
  }

  if (isError) {
    return <ErrorMessage message={error?.message ?? 'erro'} />
  }

  const entries = metrics ? Object.entries(metrics) : []
  if (entries.length === 0) {
    return <EmptyState message="Nenhum nível encontrado" />
  }

  const levels = entries.map(([name, data]) => ({
    name,
    metrics: {
      new: data.open,
      progress: (data as any).progress ?? 0,
      pending: (data as any).pending ?? 0,
      resolved: data.closed,
    },
  }))

  return <LevelsPanel levels={levels} />
}

describe('LevelsPanel states', () => {
  afterEach(() => {
    jest.resetAllMocks()
  })

  test('loading state shows skeleton', () => {
    mockedHook.mockReturnValue({
      metrics: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refreshMetrics: jest.fn(),
    })
    render(<LevelsPanelWrapper />)
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
  })

  test('error state renders ErrorMessage', () => {
    mockedHook.mockReturnValue({
      metrics: undefined,
      isLoading: false,
      isError: true,
      error: new Error('fail'),
      refreshMetrics: jest.fn(),
    })
    render(<LevelsPanelWrapper />)
    expect(screen.getByText('fail')).toBeInTheDocument()
  })

  test('empty data renders EmptyState', () => {
    mockedHook.mockReturnValue({
      metrics: {},
      isLoading: false,
      isError: false,
      error: null,
      refreshMetrics: jest.fn(),
    })
    render(<LevelsPanelWrapper />)
    expect(screen.getByText('Nenhum nível encontrado')).toBeInTheDocument()
  })

  test('valid data renders level cards', () => {
    mockedHook.mockReturnValue({
      metrics: { N1: { open: 2, closed: 3 } },
      isLoading: false,
      isError: false,
      error: null,
      refreshMetrics: jest.fn(),
    })
    render(<LevelsPanelWrapper />)
    expect(screen.getByText('N1')).toBeInTheDocument()
    expect(screen.getByText('Novos')).toBeInTheDocument()
    expect(screen.getByText('Progresso')).toBeInTheDocument()
    expect(screen.getByText('Pendente')).toBeInTheDocument()
    expect(screen.getByText('Resolvido')).toBeInTheDocument()
  })
})
