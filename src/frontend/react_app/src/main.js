import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { initializeFaro, faro } from '@grafana/faro-react';
import { TracingInstrumentation } from '@grafana/faro-web-tracing';
import { queryClient } from '@/lib/queryClient';
import App from './App';
import './index.css';
initializeFaro({
    url: import.meta.env.NEXT_PUBLIC_FARO_URL,
    app: {
        name: 'glpi-dashboard-react',
    },
    instrumentations: [new TracingInstrumentation()],
});
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(_jsx(React.StrictMode, { children: _jsxs(QueryClientProvider, { client: queryClient, children: [_jsx(React.Profiler, { id: "App", onRender: (id, phase, actualDuration) => {
                    faro.api.pushMeasurement({
                        type: 'react-render-duration',
                        values: {
                            duration: actualDuration,
                        },
                        context: { id, phase },
                    });
                }, children: _jsx(App, {}) }), import.meta.env.DEV && _jsx(ReactQueryDevtools, { initialIsOpen: false })] }) }));
