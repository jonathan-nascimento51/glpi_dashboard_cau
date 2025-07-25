import { render, screen, waitFor } from '@testing-library/react'
import App from './App'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

// Cria o client do react-query com opções padrão para teste
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

// Função auxiliar para renderizar com o provedor do react-query
function renderWithClient(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

// Mocks dos hooks e dos componentes
jest.mock('./hooks/useTickets', () => ({
  useTickets: jest.fn(),
}))
jest.mock('./hooks/useChamadosPorData', () => ({
  useChamadosPorData: jest.fn(),
}))
jest.mock('./hooks/useChamadosPorDia', () => ({
  useChamadosPorDia: jest.fn(),
}))

jest.mock('./components/Header', () => () => <header>Header Mock</header>)
jest.mock('./components/FilterPanel', () => () => <div>FilterPanel Mock</div>)
jest.mock('./components/Sidebar', () => () => <aside>Sidebar Mock</aside>)
jest.mock('./components/LevelsPanel', () => () => <div>LevelsPanel Mock</div>)

import { useTickets } from './hooks/useTickets'
import { useChamadosPorData } from './hooks/useChamadosPorData'
import { useChamadosPorDia } from './hooks/useChamadosPorDia'

const useTicketsMock = useTickets as jest.Mock
const useChamadosPorDataMock = useChamadosPorData as jest.Mock
const useChamadosPorDiaMock = useChamadosPorDia as jest.Mock

const mockTickets = [
  {
    id: 1,
    name: 'Problema na impressora',
    status: 'New',
    priority: 'High',
    date_creation: new Date().toISOString(),
  },
]

const mockChamadosPorData = [{ date: '2024-01-01', total: 10 }]
const mockChamadosPorDia = [{ date: '2024-01-01', count: 5 }]

describe('App Integration', () => {
  beforeEach(() => {
    // Limpa os mocks antes de cada teste
    useTicketsMock.mockClear()
    useChamadosPorDataMock.mockClear()
    useChamadosPorDiaMock.mockClear()
  })

  it('renders loading state initially', () => {
    useTicketsMock.mockReturnValue({
      tickets: [],
      isLoading: true,
      isSuccess: false,
      error: null,
    })
    useChamadosPorDataMock.mockReturnValue({ data: [], isLoading: true })
    useChamadosPorDiaMock.mockReturnValue({ data: [], isLoading: true })

    renderWithClient(<App />)

    // Verifica se os skeletons de carregamento são exibidos
    expect(screen.getByText(/Carregando chamados.../i)).toBeInTheDocument()
    expect(screen.getByText(/Carregando heatmap.../i)).toBeInTheDocument()
  })

  it('renders the full dashboard with data after loading', async () => {
    useTicketsMock.mockReturnValue({
      tickets: mockTickets,
      isLoading: false,
      isSuccess: true,
      error: null,
    })
    useChamadosPorDataMock.mockReturnValue({
      data: mockChamadosPorData,
      isLoading: false,
    })
    useChamadosPorDiaMock.mockReturnValue({
      data: mockChamadosPorDia,
      isLoading: false,
    })

    renderWithClient(<App />)

    // Aguarda a renderização dos dados e dos componentes lazy-loaded
    await waitFor(() => {
      // Verifica se o ticket principal foi renderizado
      expect(screen.getByText('Problema na impressora')).toBeInTheDocument()
      // Verifica se os títulos dos gráficos estão na tela
      expect(screen.getByText('Chamados por Dia')).toBeInTheDocument()
      expect(
        screen.getByText('Chamados no Ano (Heatmap Diário)'),
      ).toBeInTheDocument()
    })
  })

  it('renders error messages if data fetching fails', () => {
    useTicketsMock.mockReturnValue({
      tickets: [],
      isLoading: false,
      isSuccess: false,
      error: { message: 'Falha ao buscar tickets' },
    })
    useChamadosPorDataMock.mockReturnValue({ data: [], isLoading: false, isError: true })
    useChamadosPorDiaMock.mockReturnValue({ data: [], isLoading: false, error: true })

    renderWithClient(<App />)

    expect(screen.getByText('Falha ao buscar tickets')).toBeInTheDocument()
    expect(screen.getByText('Erro ao carregar chamados.')).toBeInTheDocument()
    expect(screen.getByText('Erro ao carregar dados do heatmap')).toBeInTheDocument()
  })
})
