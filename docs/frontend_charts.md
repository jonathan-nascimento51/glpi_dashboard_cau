# Dynamic Charts with SWR

This guide describes how to display GLPI ticket trends and heatmaps using SWR and React components.

## API Endpoints

Two REST routes provide the aggregated data used by the charts and leverage the worker's Redis cache:

- `/chamados/por-data` — returns a list of `{ "date": "YYYY-MM-DD", "total": n }` grouped by ticket creation date. The response is cached for **one hour**.
- `/chamados/por-dia` — returns the same structure for calendar heatmap totals and is cached for **24 hours**.

Both endpoints perform the aggregation server-side so the front-end only consumes summarized values.

Make sure `python worker.py` is running and set `NEXT_PUBLIC_API_BASE_URL` in
`src/frontend/react_app/.env` to point to the worker (default `http://127.0.0.1:8000`). All
requests in the examples below use this variable.

## Hooks

### `useChamadosPorData`

Fetches aggregated ticket counts per day from `/chamados/por-data`.

```ts
import useSWR from 'swr'
import { fetcher } from '../lib/swrClient'

export interface ChamadoPorData {
  date: string
  total: number
}

export function useChamadosPorData() {
  const { data, error, isLoading } = useSWR<ChamadoPorData[]>(
    '/chamados/por-data',
    fetcher,
    { refreshInterval: 60000, revalidateOnFocus: false },
  )

  return { dados: data || [], loading: isLoading, erro: error }
}

// The fetcher prefixes `NEXT_PUBLIC_API_BASE_URL` automatically,
// so `/chamados/por-data` resolves to
// `${import.meta.env.NEXT_PUBLIC_API_BASE_URL}/chamados/por-data`.
```

### `useChamadosPorDia`

Same pattern but pointing to `/chamados/por-dia` for daily totals.

## Components

### `ChamadosTendencia`

Renders a line chart with Recharts using `useChamadosPorData`.

### `ChamadosHeatmap`

Uses `react-calendar-heatmap` and `useChamadosPorDia` to display a GitHub-style calendar.

Both components show loading and error states and refresh data every minute.

## Styling

Add color classes for the heatmap in `src/index.css`:

```css
.color-empty { fill: #ebedf0; }
.color-scale-1 { fill: #c6e48b; }
.color-scale-2 { fill: #7bc96f; }
.color-scale-3 { fill: #239a3b; }
.color-scale-4 { fill: #196127; }
```

Import the components in `pages/Dashboard.tsx` to display them under the metrics section.
