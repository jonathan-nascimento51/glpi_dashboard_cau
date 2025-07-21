import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { jest } from '@jest/globals'
import { ChamadosTendencia } from '../ChamadosTendencia'
import * as useChamadosPorData from '../../hooks/useChamadosPorData'

// Mock the custom hook
jest.mock('../../hooks/useChamadosPorData')

// Mock the recharts library to avoid rendering complex SVG in tests
jest.mock('recharts', () => {
  const OriginalRecharts: typeof import('recharts') = jest.requireActual('recharts')
  return {
    ...OriginalRecharts,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="recharts-responsive-container">{children}</div>
    ),
    LineChart: ({
      children,
      data,
    }: {
      children: React.ReactNode
      data: unknown[]
    }) => (
      <div data-testid="recharts-line-chart" data-chart-data={JSON.stringify(data)}>
        {children}
      </div>
    ),
    Line: () => <div data-testid="recharts-line" />,
    XAxis: () => <div data-testid="recharts-xaxis" />,
    YAxis: () => <div data-testid="recharts-yaxis" />,
    Tooltip: () => <div data-testid="recharts-tooltip" />,
    CartesianGrid: () => <div data-testid="recharts-cartesian-grid" />,
  }
})

const mockedUseChamadosPorData = useChamadosPorData.useChamadosPorData as jest.Mock

describe('ChamadosTendencia', () => {
  beforeEach(() => {
    mockedUseChamadosPorData.mockClear()
  })

  it('should display a loading message while fetching data', () => {
    mockedUseChamadosPorData.mockReturnValue({
      isLoading: true,
      isError: false,
      data: undefined,
    })

    render(<ChamadosTendencia />)

    expect(screen.getByText('Carregando chamados...')).toBeInTheDocument()
  })

  it('should display an error message if fetching fails', () => {
    mockedUseChamadosPorData.mockReturnValue({
      isLoading: false,
      isError: true,
      data: undefined,
    })

    render(<ChamadosTendencia />)

    expect(screen.getByText('Erro ao carregar chamados.')).toBeInTheDocument()
  })

  it('should render the chart with data when fetching is successful', () => {
    const mockData = [
      { date: '2024-01-01', total: 5 },
      { date: '2024-01-03', total: 53 },
    ]
    mockedUseChamadosPorData.mockReturnValue({
      isLoading: false,
      isError: false,
      data: mockData,
    } as unknown)
    render(<ChamadosTendencia />)
    const formatted = new Date('2024-01-01').toLocaleDateString()
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })
})
