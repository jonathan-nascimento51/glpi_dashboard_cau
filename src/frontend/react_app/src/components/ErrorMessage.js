import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function ErrorMessage({ title = 'Erro', message, onRetry }) {
    return (_jsxs("div", { className: "text-center p-4 text-red-700", children: [_jsx("h2", { className: "text-xl font-semibold mb-2", children: title }), _jsx("p", { className: "mb-4", children: message }), onRetry && (_jsx("button", { onClick: onRetry, className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600", children: "Tentar novamente" }))] }));
}
