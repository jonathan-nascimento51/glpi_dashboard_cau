# Dashboard Components

## Context
The dashboard is composed of reusable React components that aggregate metrics from the GLPI API. This structure allows the UI to evolve without rewriting data logic.

## Decision
Adopt small, focused components for charts and KPI widgets. Each component receives preprocessed data from the API worker via typed props.

## Consequences
Developers can swap or extend visual elements with minimal side effects. Tests target each widget in isolation and the overall page composition remains clear.

## Steps
1. Create a `components/` folder inside the React app.
2. Write each widget as a TypeScript React component using Chart.js or shadcn/ui.
3. Expose props such as `tickets` or `sla` to keep data flow explicit.
4. Add stories or examples demonstrating usage in the dashboard layout.
