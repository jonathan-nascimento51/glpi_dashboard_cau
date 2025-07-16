# Dashboard Components

## Context
The dashboard app uses Plotly Dash to visualize GLPI service desk metrics. To
keep the interface maintainable we rely on small reusable components. Each
component renders a single KPI card or chart and wires its callbacks
internally so it can be dropped into any page layout.

## Decision
Adopt small, focused components for charts and KPI widgets. Each component receives preprocessed data from the API worker via typed props.

## Consequences
Developers can swap or extend visual elements with minimal side effects. Tests target each widget in isolation and the overall page composition remains clear.

## Steps
1. Implement each widget in `dashboard_app.py` under a function like
   `build_ticket_funnel()` returning a layout block.
2. Insert the component in the page layout and register its callbacks via
   `app.callback` in the same module. Keep callbacks scoped to the widget to
   avoid side effects across pages.
3. Extend tests in `tests/` to render the component with sample data and ensure
   it raises no exceptions or duplicate callbacks.
