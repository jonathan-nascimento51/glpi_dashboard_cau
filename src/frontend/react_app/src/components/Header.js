"use client";
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCallback } from 'react';
import { useThemeSwitcher } from '../hooks/useThemeSwitcher';
import { useFilters } from '../hooks/useFilters';
const Header = () => {
    const { theme, setTheme } = useThemeSwitcher();
    const { toggleFilters } = useFilters();
    const setLight = useCallback(() => setTheme('light'), [setTheme]);
    const setDark = useCallback(() => setTheme('dark'), [setTheme]);
    const setCorporate = useCallback(() => setTheme('corporate'), [setTheme]);
    const setTech = useCallback(() => setTheme('tech'), [setTheme]);
    return (_jsxs("header", { className: "header", children: [_jsxs("div", { className: "brand", children: [_jsx("div", { className: "brand-logo", children: _jsx("i", { className: "fas fa-microchip" }) }), _jsxs("div", { className: "brand-info", children: [_jsx("h1", { children: "Centro de Comando" }), _jsx("p", { children: "Departamento de Tecnologia" })] })] }), _jsxs("div", { className: "header-controls", children: [_jsxs("div", { className: "theme-switcher", children: [_jsx("button", { className: `theme-btn ${theme === 'light' ? 'active' : ''}`, onClick: setLight, children: "Light" }), _jsx("button", { className: `theme-btn ${theme === 'dark' ? 'active' : ''}`, onClick: setDark, children: "Dark" }), _jsx("button", { className: `theme-btn ${theme === 'corporate' ? 'active' : ''}`, onClick: setCorporate, children: "Corp" }), _jsx("button", { className: `theme-btn ${theme === 'tech' ? 'active' : ''}`, onClick: setTech, children: "Tech" })] }), _jsxs("div", { className: "search-container", children: [_jsx("i", { className: "fas fa-search search-icon" }), _jsx("input", { type: "text", className: "search-input", placeholder: "Buscar chamados, t\u00E9cnicos..." }), _jsx("div", { className: "search-results", id: "searchResults" })] }), _jsxs("div", { className: "status-live", children: [_jsx("div", { className: "live-indicator" }), _jsx("span", { children: "SISTEMA ATIVO" })] }), _jsxs("button", { className: "refresh-btn", children: [_jsx("i", { className: "fas fa-sync-alt" }), _jsx("span", { children: "Atualizar" })] }), _jsxs("button", { className: "refresh-btn", onClick: toggleFilters, children: [_jsx("i", { className: "fas fa-filter" }), _jsx("span", { children: "Filtros" })] }), _jsx("div", { className: "current-time", id: "currentTime" })] })] }));
};
export default Header;
