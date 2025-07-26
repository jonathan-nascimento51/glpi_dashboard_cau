# 0001. Front-End Stack Choice

Date: 2024-07-03

## Status

Accepted

## Context

The project requires a modern front-end stack capable of delivering high performance and maintainability. The architectural plan now recommends React with TypeScript bundled by Vite, and a testing toolchain based on Jest and Playwright.

## Decision

Adopt **Vite** with React 18 and TypeScript 5 as the baseline. Use Jest for unit tests, Playwright for end-to-end tests, and Storybook for UI development. This combination provides strong typing, fast builds and a rich ecosystem of tools.

The switch away from Next.js reduces complexity since server-side rendering is not required for the dashboard. Vite offers faster iteration times and simpler configuration.

## Consequences

All front-end code will follow the Feature-Sliced Design (FSD) structure. The toolchain will enforce linting and formatting via ESLint and Prettier. Future decisions around state management and data fetching libraries will extend this ADR.
