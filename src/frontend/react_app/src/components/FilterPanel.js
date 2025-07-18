"use client";
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCallback } from 'react';
import { useFilters } from '../hooks/useFilters.js';
const FilterPanel = () => {
    const { filters, toggleFilters, toggleValue } = useFilters();
    const renderOptions = useCallback((category) => {
        const values = filters[category];
        return values.map((value) => (_jsxs("div", { className: "filter-option", onClick: () => toggleValue(category, value), children: [_jsx("div", { className: `filter-checkbox ${values.includes(value) ? 'checked' : ''}`, children: _jsx("i", { className: "fas fa-check" }) }), _jsx("div", { className: "filter-label", children: value })] }, value)));
    }, [filters, toggleValue]);
    return (_jsxs("div", { className: `filter-panel ${filters.open ? 'open' : ''}`, id: "filterPanel", children: [_jsxs("div", { className: "filter-header", children: [_jsx("div", { className: "filter-title", children: "Filtros Avan\u00E7ados" }), _jsx("button", { className: "filter-close", onClick: toggleFilters, title: 'Fechar filtros', children: _jsx("i", { className: "fas fa-times" }) })] }), _jsxs("div", { className: "filter-group", children: [_jsx("div", { className: "filter-group-title", children: "Per\u00EDodo" }), _jsx("div", { className: "filter-options", children: renderOptions('period') })] }), _jsxs("div", { className: "filter-group", children: [_jsx("div", { className: "filter-group-title", children: "N\u00EDveis" }), _jsx("div", { className: "filter-options", children: renderOptions('level') })] }), _jsxs("div", { className: "filter-group", children: [_jsx("div", { className: "filter-group-title", children: "Status" }), _jsx("div", { className: "filter-options", children: renderOptions('status') })] }), _jsxs("div", { className: "filter-group", children: [_jsx("div", { className: "filter-group-title", children: "Prioridade" }), _jsx("div", { className: "filter-options", children: renderOptions('priority') })] })] }));
};
export default FilterPanel;
