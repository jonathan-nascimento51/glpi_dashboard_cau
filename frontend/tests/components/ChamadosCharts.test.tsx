import { render, screen } from '@testing-library/react'
import { ChamadosTendencia } from '@/components/ChamadosTendencia'
import { ChamadosHeatmap } from '@/components/ChamadosHeatmap'
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
  mockedData.useChamadosPorData.mockReturnValue({ dados: [], isLoading: true, error: null })
  render(<ChamadosTendencia />)
  expect(screen.getByText('Carregando tendência...')).toBeInTheDocument()
})

test('ChamadosTendencia error', () => {
  mockedData.useChamadosPorData.mockReturnValue({ dados: [], isLoading: false, error: new Error('tendencia fail') })
  render(<ChamadosTendencia />)
  expect(screen.getByText('tendencia fail')).toBeInTheDocument()
})

test('ChamadosHeatmap success', () => {
  mockedDia.useChamadosPorDia.mockReturnValue({ dados: [{ date: '2024-01-01', total: 2 }], isLoading: false, error: null })
  render(<ChamadosHeatmap />)
  expect(screen.getByText('Chamados no Ano (Heatmap Diário)')).toBeInTheDocument()
})

test('ChamadosHeatmap error', () => {
  mockedDia.useChamadosPorDia.mockReturnValue({ dados: [], isLoading: false, error: new Error('fail') })
  render(<ChamadosHeatmap />)
  expect(screen.getByText('Erro ao carregar dados do heatmap')).toBeInTheDocument()
})

