# Front-End Architecture Guide

This document summarizes the high level guidelines for implementing the dashboard front-end with a high technical standard.

## 1. Principles

- **Alignment with business**: every UI feature must map back to a real service-desk need.
- **Component based design**: build reusable pieces and organize folders by feature.
- **Quality gates**: apply lint, type checking and automated tests for every change.
- **Performance and security**: follow Core Web Vitals targets and OWASP recommendations.

## 2. Recommended Stack

- **Framework**: React with TypeScript for strong typing and large ecosystem.
- **Styling**: Tailwind CSS or CSS-in-JS for scoped and consistent styles.
- **Testing**: Jest for unit tests, React Testing Library for components and Playwright for end-to-end flows.
- **CI**: reuse the existing GitHub Actions workflow running lint (`eslint` and `prettier`), unit tests and E2E tests.

## 3. Structure

```text
src/frontend/react_app/
├── src/
│   ├── features/             # slices of business logic
│   ├── components/           # shared UI components
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
└── package.json
```

- **features/** contains domain oriented modules (e.g. `tickets`, `analytics`).
- **components/** hosts reusable building blocks such as KPI cards and charts.

## 4. Testing Strategy

Follow the testing pyramid:

1. **Unit tests** for each component and hook using Jest.
2. **Integration tests** that interact with the real API using Docker containers.
3. **End-to-end tests** using Playwright to cover the main user journeys.

## 5. Next Steps

1. Scaffold a Vite React project inside the `src/frontend/react_app` directory.
2. Implement the first feature slice for displaying ticket statistics.
3. Configure GitHub Actions to run npm CI alongside the existing Python pipeline.

## 6. Running the Front-End

Follow these steps inside the `src/frontend/react_app` folder to start developing:

```bash
cd src/frontend/react_app
nvm install         # installs the version pinned in .nvmrc
nvm use
mise settings add idiomatic_version_file_enable_tools node  # or disable idiomatic files
npm install         # installs dotenv, @eslint/js and other dev dependencies
# npm ci can be used for reproducible installs
npm run dev         # launch Vite dev server
```

Make sure the dependencies are installed before running any npm script so tests
and lint work correctly.

Additional useful commands:

```bash
npm run build       # production build
npm test            # run Jest unit tests
npm run test:e2e    # run Playwright E2E tests
npm run lint        # check code style with ESLint
npx prettier --write "src/**/*.{ts,tsx}"  # format code
```

### Environment Variables

Create a `.env` file in the `src/frontend/react_app` directory to configure the URL of the worker API. This value must be provided in **development**, **testing** and **production** environments:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

If this variable is missing the application will fail to start. The fetcher
responsible for API calls verifies that `NEXT_PUBLIC_API_BASE_URL` is defined
 and throws an error otherwise. `npm run dev`, `npm test`, `npm run build` and
 `npm run preview` automatically execute `npm run check-env` to validate the
 configuration. This script imports the shared logic from `scripts/check-env.js`
 at the project root, so you can also run `npm run check-env` manually before
 launching the app or building for production.

The React code can read this value using `import.meta.env.NEXT_PUBLIC_API_BASE_URL` to send requests to the worker.

> **Note**: this variable was renamed from `VITE_API_URL` to `NEXT_PUBLIC_API_BASE_URL` to match Next.js conventions. This change ensures compatibility with Next.js, which uses the `NEXT_PUBLIC_` prefix for environment variables exposed to the browser.

Vite only exposes variables prefixed with `VITE_` by default. The project configures `envPrefix` in `vite.config.ts` so that `NEXT_PUBLIC_*` variables are also loaded.

Imports reference `@/` as a shortcut to the `src/` folder. Both Vite and TypeScript resolve this alias through `resolve.alias` in `vite.config.ts` and the `paths` option in `tsconfig.app.json`.

### API Integration

Start the worker with `python worker.py` (it listens on port `8000` by default) and point the front-end to it using the `NEXT_PUBLIC_API_BASE_URL` variable. The `/tickets` endpoint now returns the `priority` as a string. Example fetching ticket metrics:

```ts
const resp = await fetch(`${import.meta.env.NEXT_PUBLIC_API_BASE_URL}/tickets/metrics`);
const data = await resp.json();
```

The worker also streams progress using `/tickets/stream`:

```ts
const url = `${import.meta.env.NEXT_PUBLIC_API_BASE_URL}/tickets/stream`;
const es = new EventSource(url);
es.onmessage = (ev) => console.log('chunk', ev.data);
```

For aggregated statistics the worker offers `/metrics/aggregated`. This endpoint
returns cached counts grouped by status and technician, enabling dashboards to
load summary values quickly.

Jest and Playwright tests rely on this same URL when exercising real API calls, so ensure the worker is running before executing `npm test` or `npm run test:e2e`.

### Refactoring TypeScript imports

When the front-end files were reorganised into `src/frontend/react_app`, existing TypeScript imports pointing to the old `frontend/src` paths needed adjustment. The script `scripts/refactor/update_ts_imports.js` automates this process using jscodeshift. It reads `file_map.json` to map old locations to the new `@/` alias and updates all matching `import` statements.

Run it from the repository root after moving files:

```bash
jscodeshift -t scripts/refactor/update_ts_imports.js <paths> --map file_map.json
```

Pass one or more files or directories as `<paths>` to transform.

For small moves you can also invoke the helper script `scripts/run_ts_codemod.sh`.
It reads `file_map.json`, moves each file with `git mv` and runs the codemod
`scripts/update-imports.js` with the appropriate `--oldPath` and `--newPath`
options to update import statements automatically.


### Faro instrumentation

Install the React tracing packages so the dashboard can report web vitals:

```bash
npm install @grafana/faro-react @grafana/faro-web-tracing
```

Create `NEXT_PUBLIC_FARO_URL` in `src/frontend/react_app/.env` pointing to the
Faro collector. `src/main.tsx` reads this value, initializes the client and
wraps `App` inside `React.Profiler` to push render timings via
`faro.api.pushMeasurement`.

Refer to [docs/observability.md](observability.md) for a complete example of
the configuration and dashboard.

### Storybook

Execute o Storybook para visualizar componentes isoladamente. Dentro de
`src/frontend/react_app`, execute:

```bash
npm run storybook      # inicia em http://localhost:6006
npm run build-storybook  # gera a versão estática em storybook-static/
```

Use these stories to validate different loading states and to document props
automatically via the `autodocs` tag.

## 7. Code generation with Plop

Reusable boilerplate for new React components and Dash modules is created with
[Plop](https://plopjs.com/). After installing dependencies you can run the
generators from the repository root:

```bash
npx plop react-component
npx plop dash-module
```

`react-component` scaffolds a folder under
`src/frontend/react_app/src/components/` containing a `.tsx` file, CSS module,
`index.ts` barrel and a Jest test. `dash-module` writes a Python file inside
`src/backend/components/` with stubbed `layout()` and `register_callbacks(app)`
functions so you can hook it into the Dash application.
