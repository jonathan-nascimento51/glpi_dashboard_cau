import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useTicketMetrics } from './api';
import { StatsCard } from '../../widgets/stats/StatsCard';
export function TicketStatsPage() {
    const { data, isLoading, error } = useTicketMetrics();
    if (isLoading)
        return _jsx("div", { children: "Loading..." });
    if (error)
        return _jsx("div", { children: error.message });
    return (_jsxs("div", { className: "grid gap-4 grid-cols-3", children: [_jsx(StatsCard, { label: "Total", value: data.total }), _jsx(StatsCard, { label: "Opened", value: data.opened }), _jsx(StatsCard, { label: "Closed", value: data.closed })] }));
}
