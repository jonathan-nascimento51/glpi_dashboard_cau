# Dashboard Components

## Context
The dashboard app uses Plotly Dash to visualize GLPI service desk metrics. To
keep the interface maintainable we rely on small reusable components.

## Decision
Create dedicated Python modules for each chart and card. Use Dash `dcc.Graph`
for visualizations and encapsulate callbacks inside the component class.

## Consequences
Components can be composed freely across pages. Complexity is reduced but
developers must register callbacks when wiring new components.

## Steps
1. Implement each widget in `dashboard_app.py` under a function like
   `build_ticket_funnel()` returning a layout block.
2. Insert the component in the page layout and register its callbacks via
   `app.callback` in the same module.
3. Extend tests in `tests/` to render the component with sample data and ensure
   it raises no exceptions.
