import { render, screen } from '@testing-library/react'
import ChamadosTendencia from '@/components/ChamadosTendencia'
import ChamadosHeatmap from '@/components/ChamadosHeatmap'
import * as dataHook from '@/hooks/useChamadosPorData'
import * as diaHook from '@/hooks/useChamadosPorDia'

jest.mock('@/hooks/useChamadosPorData')
jest.mock('@/hooks/useChamadosPorDia')

const mockedData = dataHook as jest.Mocked<typeof dataHook>
const mockedDia = diaHook as jest.Mocked<typeof diaHook>

beforeEach(() => {
  jest.resetAllMocks()
})

test('ChamadosTendencia loading', () => {
  mockedData.useChamadosPorData.mockReturnValue({
    data: [],
    isLoading: true,
    isError: false,
    status: 'loading',
  } as any)
  render(<ChamadosTendencia />)
  expect(screen.getByText('Carregando chamados...')).toBeInTheDocument()
})

test('ChamadosTendencia error', () => {
  mockedData.useChamadosPorData.mockReturnValue({
    data: [],
    isLoading: false,
    isError: true,
    status: 'error',
  } as any)
  render(<ChamadosTendencia />)
  expect(screen.getByText('Erro ao carregar chamados.')).toBeInTheDocument()
})

test('ChamadosHeatmap success', () => {
  mockedDia.useChamadosPorDia.mockReturnValue({ data: [{ date: '2024-01-01', total: 2 }], isLoading: false, error: null })
  render(<ChamadosHeatmap />)
  expect(screen.getByText('Chamados no Ano (Heatmap Diário)')).toBeInTheDocument()
})

test('ChamadosHeatmap error', () => {
  mockedDia.useChamadosPorDia.mockReturnValue({ data: [], isLoading: false, error: new Error('fail') })
  render(<ChamadosHeatmap />)
  expect(screen.getByText('Erro ao carregar dados do heatmap')).toBeInTheDocument()
})
