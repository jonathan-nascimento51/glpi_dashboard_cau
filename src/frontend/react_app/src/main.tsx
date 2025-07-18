import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { initializeFaro, faro } from '@grafana/faro-react'
import { TracingInstrumentation } from '@grafana/faro-web-tracing'
import { queryClient } from '@/lib/queryClient.js'
import App from './App.js'
import './index.css'

initializeFaro({
  url: import.meta.env.NEXT_PUBLIC_FARO_URL,
  app: {
    name: 'glpi-dashboard-react',
  },
  instrumentations: [new TracingInstrumentation()],
})


const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
)

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <React.Profiler
        id="App"
        onRender={(id, phase, actualDuration) => {
          faro.api.pushMeasurement({
            type: 'react-render-duration',
            values: {
              duration: actualDuration,
            },
            context: { id, phase },
          });
        }}
      >
        <App />
      </React.Profiler>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>,
)
