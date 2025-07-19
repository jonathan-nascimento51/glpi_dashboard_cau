import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { memo } from 'react';
import { useChamadosPorData } from '../hooks/useChamadosPorData';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
function ChamadosTendenciaComponent() {
    const { dados, isLoading, error } = useChamadosPorData();
    if (isLoading)
        return _jsx("div", { children: "Carregando tend\u00EAncia..." });
    if (error)
        return _jsx("div", { children: "Erro ao carregar dados de tend\u00EAncia" });
    return (_jsxs("div", { className: "bg-white dark:bg-gray-800 p-4 rounded shadow w-full", children: [_jsx("h2", { className: "text-xl font-semibold mb-2", children: "Chamados por Dia" }), _jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(LineChart, { data: dados, margin: { top: 20, right: 30, left: 0, bottom: 0 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "date", tick: { fontSize: 12 } }), _jsx(YAxis, {}), _jsx(Tooltip, {}), _jsx(Line, { type: "monotone", dataKey: "total", stroke: "#8884d8", strokeWidth: 2 })] }) })] }));
}
export const ChamadosTendencia = memo(ChamadosTendenciaComponent);
