import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { jest } from '@jest/globals'

jest.mock('../hooks/useTickets', () => ({
  useTickets: jest.fn(),
}))

import TicketsDisplay from './TicketsDisplay'
import { useTickets } from '../hooks/useTickets'

const useTicketsMock = useTickets as jest.Mock

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

  it('deve paginar os tickets corretamente', () => {
    const mockTickets = Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      name: `Ticket ${i + 1}`,
    }))

    useTicketsMock.mockReturnValue({
      tickets: mockTickets,
      error: undefined,
      isLoading: false,
      isSuccess: true,
      refreshTickets: jest.fn(),
    })

    render(<TicketsDisplay />)

    expect(screen.getByText('Ticket 1')).toBeInTheDocument()
    expect(screen.queryByText('Ticket 16')).not.toBeInTheDocument()

    fireEvent.click(screen.getByLabelText('Próxima página'))

    expect(screen.getByText('Ticket 16')).toBeInTheDocument()
    expect(screen.queryByText('Ticket 1')).not.toBeInTheDocument()
  })
})
