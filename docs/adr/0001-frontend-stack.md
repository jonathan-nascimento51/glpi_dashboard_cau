# 0001. Front-End Stack Choice

Date: 2024-07-03

## Status
Accepted

## Context
The project requires a modern front-end stack capable of delivering high performance and maintainability. The architectural plan recommends React with TypeScript, Next.js for server-side rendering, and a testing toolchain based on Jest and Playwright.

## Decision
Adopt Next.js 15 with React 19 and TypeScript 5 as the baseline. Use Jest for unit tests, Playwright for end-to-end tests, and Storybook for UI development. This combination provides strong typing, fast builds and a rich ecosystem of tools.

## Consequences
All front-end code will follow the Feature-Sliced Design (FSD) structure. The toolchain will enforce linting and formatting via ESLint and Prettier. Future decisions around state management and data fetching libraries will extend this ADR.
