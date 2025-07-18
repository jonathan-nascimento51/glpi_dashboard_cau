import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { memo } from 'react';
const MetricCardComponent = ({ type, value, change, onClick, canvasRef, }) => {
    const sign = change >= 0 ? 'positive' : 'negative';
    const changeText = `${change > 0 ? '+' : ''}${change}%`;
    return (_jsxs("div", { className: "metric-card", onClick: onClick, "data-type": type, children: [_jsxs("div", { className: "metric-header", children: [_jsx("div", { className: `metric-icon ${type}`, children: _jsx("i", { className: "fas fa-circle" }) }), _jsxs("div", { className: `metric-change ${sign}`, children: [_jsx("i", { className: `fas fa-arrow-${change >= 0 ? 'up' : 'down'}` }), _jsx("span", { children: changeText })] })] }), _jsx("div", { className: "metric-value", children: value }), _jsxs("div", { className: "metric-label", children: [type === 'new' && 'Novos Chamados', type === 'pending' && 'Pendentes', type === 'progress' && 'Em Progresso', type === 'resolved' && 'Resolvidos'] }), _jsx("canvas", { className: "metric-sparkline", ref: canvasRef })] }));
};
export const MetricCard = memo(MetricCardComponent);
