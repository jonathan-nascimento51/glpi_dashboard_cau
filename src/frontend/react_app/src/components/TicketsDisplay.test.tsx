import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { jest } from '@jest/globals'

jest.unstable_mockModule('@/hooks/useTickets', () => ({
  useTickets: jest.fn(),
}))

let TicketsDisplay: typeof import('./TicketsDisplay').default
let useTicketsMock: jest.Mock

beforeAll(async () => {
  const mod = await import('../hooks/useTickets')
  useTicketsMock = mod.useTickets as jest.Mock
  const { default: TicketsDisplayModule } = await import('./TicketsDisplay')
  TicketsDisplay = TicketsDisplayModule
})

describe('TicketsDisplay Component', () => {
  beforeEach(() => {
    useTicketsMock.mockClear()
  })

  it('deve exibir um spinner de carregamento enquanto os dados estão sendo buscados', () => {
    useTicketsMock.mockReturnValue({
      tickets: undefined,
      error: undefined,
      isLoading: true,
      isSuccess: false,
      refreshTickets: jest.fn(),
    })

    render(<TicketsDisplay />)

    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText(/carregando/i)).toBeInTheDocument()
  })

  it('deve exibir uma mensagem de erro se a busca falhar', () => {
    const refreshSpy = jest.fn()
    useTicketsMock.mockReturnValue({
      tickets: undefined,
      error: new Error('Falha na API'),
      isLoading: false,
      isSuccess: false,
      refreshTickets: refreshSpy,
    })

    render(<TicketsDisplay />)

    expect(screen.getByText(/erro ao carregar os chamados/i)).toBeInTheDocument()
    expect(screen.getByText(/falha na api/i)).toBeInTheDocument()
    const retryBtn = screen.getByRole('button', { name: /tentar novamente/i })
    retryBtn.click()
    expect(refreshSpy).toHaveBeenCalled()
  })

  it('deve exibir uma mensagem de "nenhum chamado encontrado" se a API retornar uma lista vazia', () => {
    const refreshSpy = jest.fn()
    useTicketsMock.mockReturnValue({
      tickets: [],
      error: undefined,
      isLoading: false,
      isSuccess: true,
      refreshTickets: refreshSpy,
    })

    render(<TicketsDisplay />)

    expect(screen.getByRole('heading', { name: /nenhum chamado encontrado/i })).toBeInTheDocument()
    screen.getByRole('button', { name: /atualizar/i }).click();
    expect(refreshSpy).toHaveBeenCalled()
  })

  it('deve renderizar a tabela de tickets quando os dados são recebidos com sucesso', () => {
    const mockTickets = [
      { id: 1, name: 'Problema na impressora', status: 'New', priority: 'High' },
      { id: 2, name: 'Rede lenta', status: 'Open', priority: 'Low' },
    ]

    useTicketsMock.mockReturnValue({
      tickets: mockTickets,
      error: undefined,
      isLoading: false,
      isSuccess: true,
      refreshTickets: jest.fn(),
    })

    render(<TicketsDisplay />)

    expect(screen.getByText(/dashboard de chamados glpi/i)).toBeInTheDocument()
    expect(screen.getByText(/problema na impressora/i)).toBeInTheDocument()
    expect(screen.getByText(/rede lenta/i)).toBeInTheDocument()
    expect(screen.getByRole('table')).toBeInTheDocument()
  })
})
