import React from 'react';
import ReactDOM from 'react-dom/client';
import { initializeFaro } from '@grafana/faro-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import App from './App';
import './index.css';

const queryClient = new QueryClient();
const faroURL = import.meta.env.NEXT_PUBLIC_FARO_URL;

// Only initialize Faro if the URL is configured.
// This prevents connection errors in local development when the collector is not running.
if (faroURL && faroURL.startsWith('http')) {
  initializeFaro({
    url: faroURL,
    app: {
      name: 'glpi-dashboard-frontend',
      version: '1.0.0',
    },
  });
} else {
  console.log('Grafana Faro is not configured, skipping initialization.');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>,
);
