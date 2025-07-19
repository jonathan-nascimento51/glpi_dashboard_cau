import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useTickets } from '@/hooks/useTickets';
import { TicketTable } from './TicketTable.js';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage.js';
export function TicketsDisplay() {
    const { tickets, error, isLoading, refreshTickets } = useTickets();
    if (isLoading) {
        return _jsx(LoadingSpinner, {});
    }
    if (error) {
        return (_jsx(ErrorMessage, { title: "Erro ao carregar os chamados", message: error.message || 'Não foi possível conectar à API. Tente novamente mais tarde.', onRetry: refreshTickets }));
    }
    if (!tickets || tickets.length === 0) {
        return (_jsxs("div", { className: "text-center p-8", children: [_jsx("h2", { className: "text-xl font-semibold", children: "Nenhum chamado encontrado" }), _jsx("p", { className: "text-gray-500", children: "N\u00E3o h\u00E1 chamados para exibir no momento." }), _jsx("button", { onClick: () => refreshTickets(), className: "mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600", children: "Atualizar" })] }));
    }
    return (_jsxs("div", { children: [_jsx("h1", { className: "text-2xl font-bold mb-4", children: "Dashboard de Chamados GLPI" }), _jsx(TicketTable, { tickets: tickets })] }));
}
