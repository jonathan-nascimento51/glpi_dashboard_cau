import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function LoadingSpinner() {
    return (_jsxs("div", { className: "flex justify-center items-center p-4", role: "status", "aria-live": "polite", children: [_jsx("span", { className: "animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" }), _jsx("span", { className: "sr-only", children: "Carregando..." })] }));
}
