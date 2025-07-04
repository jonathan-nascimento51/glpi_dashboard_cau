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

```
frontend/
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

1. Scaffold a Vite React project inside the `frontend` directory.
2. Implement the first feature slice for displaying ticket statistics.
3. Configure GitHub Actions to run npm CI alongside the existing Python pipeline.

## 6. Running the Front-End

Follow these steps inside the `frontend` folder to start developing:

```bash
cd frontend
npm install         # install dependencies
npm run dev         # launch Vite dev server
```

Additional useful commands:

```bash
npm run build       # production build
npm test            # run Jest unit tests
npm run test:e2e    # run Playwright E2E tests
npm run lint        # check code style with ESLint
npx prettier --write "src/**/*.{ts,tsx}"  # format code
```

### Environment Variables

Create a `.env` file in the `frontend` directory to configure the URL of the worker API:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The React code can read this value using `import.meta.env.NEXT_PUBLIC_API_BASE_URL` to send requests to the worker.

> **Note**: previous revisions referenced `VITE_API_URL`. The variable name was updated to `NEXT_PUBLIC_API_BASE_URL` to match Next.js conventions.

### API Integration

Start the worker with `python worker.py` (it listens on port `8000` by default) and point the front-end to it using the `NEXT_PUBLIC_API_BASE_URL` variable. Example fetching ticket metrics:

```ts
const resp = await fetch(`${import.meta.env.NEXT_PUBLIC_API_BASE_URL}/tickets/metrics`);
const data = await resp.json();
```

For aggregated statistics the worker offers `/metrics/aggregated`. This endpoint
returns cached counts grouped by status and technician, enabling dashboards to
load summary values quickly.

Jest and Playwright tests rely on this same URL when exercising real API calls, so ensure the worker is running before executing `npm test` or `npm run test:e2e`.
