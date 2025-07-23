import { render, screen } from '@testing-library/react';
import { TicketTable } from '../TicketTable';

// Mock do componente de virtualização para simplificar o teste
jest.mock('../VirtualizedTicketTable', () => ({
  VirtualizedTicketTable: ({ rows }: { rows: any[] }) => (
    <div data-testid="virtualized-table">
      {rows.map(row => (
        <div key={row.id}>{row.name}</div>
      ))}
    </div>
  ),
}));

describe('TicketTable', () => {
  it('deve exibir uma mensagem quando nenhum chamado for encontrado', () => {
    render(<TicketTable tickets={[]} />);

    expect(screen.getByText('Nenhum chamado encontrado.')).toBeInTheDocument();
  });

  it('deve renderizar a tabela com os dados dos chamados', async () => {
    const mockTickets = [
      { id: 1, name: 'Problema na impressora', status: 'new', priority: 3 },
      { id: 2, name: 'PC não liga', status: 'assigned', priority: 5 },
    ];

    render(<TicketTable tickets={mockTickets as any} />);

    expect(screen.getByTestId('virtualized-table')).toBeInTheDocument();
    expect(screen.getByText('Problema na impressora')).toBeInTheDocument();
    expect(screen.getByText('PC não liga')).toBeInTheDocument();
  });
});
