import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import TicketsDisplay from '../../src/components/TicketsDisplay'

// 1. Mockamos o componente filho que agora lida com toda a lógica.
// O teste do TicketsDisplay não precisa saber como o GlpiTicketsTable funciona,
// apenas que ele é renderizado.
jest.mock('./GlpiTicketsTable', () => ({
  GlpiTicketsTable: () => (
    <div data-testid="glpi-tickets-table-mock">Mocked GlpiTicketsTable</div>
  ),
}))

describe('TicketsDisplay Component', () => {
  it('deve renderizar o título e o componente da tabela de chamados', () => {
    render(<TicketsDisplay />)
    // 2. Verifica se o título principal do dashboard é renderizado.
    const heading = screen.getByRole('heading', {
      name: /dashboard de chamados glpi/i,
    })
    expect(heading).toBeInTheDocument()
    // 3. Verifica se o componente GlpiTicketsTable (mockado) está na tela.
    expect(screen.getByTestId('glpi-tickets-table-mock')).toBeInTheDocument()
  })
})

// Os testes de loading, error, empty state e paginação foram removidos
// pois essa lógica foi movida para dentro do GlpiTicketsTable e
// deve ser testada lá.
