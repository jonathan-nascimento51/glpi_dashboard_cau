import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen } from '@testing-library/react';
import { TicketTable } from '@/components/TicketTable.js';
import React from 'react';
jest.mock('react-window', () => {
    return {
        FixedSizeList: jest.fn((props) => (_jsx("div", { "data-testid": "virtual-list", children: Array.from({ length: props.itemCount }).map((_, idx) => React.createElement(props.children, {
                index: idx,
                style: {},
                data: props.itemData,
            })) }))),
    };
}, { virtual: true });
const ticket = {
    id: 1,
    name: 'Chamado muito longo com titulo extensivo que precisa ser truncado',
    status: 'New',
    priority: 'High',
    date_creation: new Date('2023-10-27T10:00:00Z'),
};
describe('TicketTable formatting', () => {
    it('formats date and applies styles', () => {
        render(_jsx(TicketTable, { tickets: [ticket] }));
        const titleCell = screen.getByText(ticket.name);
        expect(titleCell).toHaveAttribute('title', ticket.name);
        expect(screen.getByText('High')).toHaveClass('text-red-600');
        const formatted = new Intl.DateTimeFormat('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'short',
        }).format(ticket.date_creation);
        expect(screen.getByText(formatted)).toBeInTheDocument();
    });
});
