import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { VirtualizedTicketTable } from './VirtualizedTicketTable.js';
export function TicketTable({ tickets }) {
    return (_jsxs("div", { className: "border rounded", "aria-label": "Lista de chamados", children: [_jsx("div", { role: "rowgroup", children: _jsxs("div", { className: "grid grid-cols-[80px_auto_120px_100px_160px] bg-gray-50 px-2 py-1 text-sm font-semibold", role: "row", children: [_jsx("div", { role: "columnheader", children: "ID" }), _jsx("div", { role: "columnheader", children: "T\u00EDtulo" }), _jsx("div", { role: "columnheader", children: "Status" }), _jsx("div", { role: "columnheader", children: "Prioridade" }), _jsx("div", { role: "columnheader", children: "Criado em" })] }) }), _jsx(VirtualizedTicketTable, { rows: tickets, rowHeight: 40 })] }));
}
