import { render, screen } from '@testing-library/react'
import Dashboard from '@/pages/Dashboard'

jest.mock('@/hooks/useDashboardData', () => ({
  useDashboardData: () => ({
    metrics: { new: 2, pending: 1, progress: 3, resolved: 4 },
    sparkRefs: {
      new: { current: null },
      pending: { current: null },
      progress: { current: null },
      resolved: { current: null },
    },
    refreshMetrics: jest.fn(),
    isLoading: false,
    error: null,
  }),
}))

jest.mock('@/hooks/useTickets', () => ({
  useTickets: () => ({ tickets: [{ id: 1, name: 'foo' }], isLoading: false, error: null }),
}))

jest.mock('@/components/ChamadosTendencia', () => ({
  ChamadosTendencia: () => <div>tendencia</div>,
}))

jest.mock('@/components/ChamadosHeatmap', () => ({
  ChamadosHeatmap: () => <div>heatmap</div>,
}))

jest.mock('@/hooks/useChamadosPorData', () => ({
  useChamadosPorData: () => ({ dados: [], isLoading: false, error: null }),
}))

jest.mock('@/hooks/useChamadosPorDia', () => ({
  useChamadosPorDia: () => ({ dados: [], isLoading: false, error: null }),
}))

test('renders metrics and tickets from hooks', () => {
  render(<Dashboard />)
  expect(screen.getByText('Novos Chamados')).toBeInTheDocument()
  expect(screen.getByText('foo')).toBeInTheDocument()
})
