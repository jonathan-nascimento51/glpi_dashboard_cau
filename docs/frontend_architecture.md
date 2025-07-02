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
