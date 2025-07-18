import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function StatsCard({ label, value }) {
    return (_jsxs("div", { className: "p-4 bg-white rounded shadow text-center", children: [_jsx("div", { className: "text-2xl font-bold", "data-testid": "stats-value", children: value }), _jsx("div", { className: "text-gray-500", "data-testid": "stats-label", children: label })] }));
}
