# Dynamic Charts with SWR

This guide describes how to display GLPI ticket trends and heatmaps using SWR and React components.

## API Endpoints

Two REST routes provide the aggregated data used by the charts:

- `/chamados/por-data` — returns a list of `{ "date": "YYYY-MM-DD", "total": n }` grouped by ticket creation date.
- `/chamados/por-dia` — returns the same structure for calendar heatmap totals.

Both endpoints perform the aggregation server-side so the front-end only consumes summarized values.

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
