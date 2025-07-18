import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Header from './components/Header.js';
import { ChamadosTendencia } from './components/ChamadosTendencia.js';
export default function App() {
    return (_jsxs("div", { className: "dashboard-container", children: [_jsx(Header, {}), _jsxs("main", { className: "p-4", children: [_jsx("h1", { className: "text-2xl font-bold mb-4", children: "GLPI Dashboard" }), _jsx(ChamadosTendencia, {})] })] }));
}
