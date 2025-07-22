import { render, screen } from '@testing-library/react';
import { TicketTable } from '../TicketTable';
import { useApiQuery } from '../../hooks/useApiQuery';

// Mock do hook useApiQuery
jest.mock('../hooks/useApiQuery');
const mockedUseApiQuery = useApiQuery as jest.Mock;

// Mock do componente de virtualização para simplificar o teste
jest.mock('./VirtualizedTicketTable', () => ({
  VirtualizedTicketTable: ({ rows }: { rows: any[] }) => (
    <div data-testid="virtualized-table">
      {rows.map(row => (
        <div key={row.id}>{row.name}</div>
      ))}
    </div>
  ),
}));

describe('TicketTable', () => {
  beforeEach(() => {
    // Limpa os mocks antes de cada teste
    mockedUseApiQuery.mockClear();
  });

  it('deve exibir a mensagem de carregamento enquanto os dados são buscados', () => {
    mockedUseApiQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(<TicketTable />);

    expect(screen.getByText('Carregando chamados...')).toBeInTheDocument();
  });

  it('deve exibir uma mensagem de erro se a busca falhar', () => {
    const errorMessage = 'Falha na rede';
    mockedUseApiQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: errorMessage,
    });

    render(<TicketTable />);

    expect(screen.getByText(`Erro ao carregar dados: ${errorMessage}`)).toBeInTheDocument();
  });

  it('deve exibir uma mensagem quando nenhum chamado for encontrado', () => {
    mockedUseApiQuery.mockReturnValue({
      data: { tickets: [] },
      isLoading: false,
      error: null,
    });

    render(<TicketTable />);

    expect(screen.getByText('Nenhum chamado encontrado.')).toBeInTheDocument();
  });

  it('deve renderizar a tabela com os dados dos chamados quando a busca for bem-sucedida', async () => {
    const mockTickets = [
      { id: 1, name: 'Problema na impressora', status: 'new', priority: 3, date_creation: new Date().toISOString() },
      { id: 2, name: 'PC não liga', status: 'assigned', priority: 5, date_creation: new Date().toISOString() },
    ];
    mockedUseApiQuery.mockReturnValue({
      data: { tickets: mockTickets },
      isLoading: false,
      error: null,
    });

    render(<TicketTable />);

    // Verifica se a tabela virtualizada está presente
    expect(screen.getByTestId('virtualized-table')).toBeInTheDocument();
    // Verifica se os nomes dos tickets estão no documento (simulando a renderização da tabela)
    expect(screen.getByText('Problema na impressora')).toBeInTheDocument();
    expect(screen.getByText('PC não liga')).toBeInTheDocument();
  });
});
