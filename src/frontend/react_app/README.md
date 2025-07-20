# GLPI Dashboard React App

This folder contains the React front-end of the **GLPI Dashboard CAU**. The application visualizes service desk metrics such as backlog size, SLA compliance and technician productivity. All data comes from the worker API exposed by `python worker.py`.

## Setup

1. Copy `.env.example` to `.env` and set `NEXT_PUBLIC_API_BASE_URL` to the worker address.

2. (Optional) If you are running the Grafana observability stack, also set `NEXT_PUBLIC_FARO_URL` to point to your Faro collector (e.g., `http://localhost:1234/collect`). If you are not running the collector, leave this variable commented out to avoid connection errors in the browser console.

3. Install Node dependencies with:

```bash
npm ci
```

3. Start the local dev server:

```bash
npm run dev
```

In development mode, React Query Devtools are automatically enabled, so you can
inspect queries without manual configuration.

The devtools component is mounted in `main.tsx` and guarded by `import.meta.env.DEV`, ensuring it is excluded from production builds.

Node.js 20 is expected. Run the commands from inside `src/frontend/react_app`.

See the [frontend architecture guide](../../docs/frontend_architecture.md) for advanced configuration, environment variables and available npm scripts.
