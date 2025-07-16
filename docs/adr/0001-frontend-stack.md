# 0001. Front-End Stack Choice

Date: 2024-07-03

## Status

Accepted

## Context

The project requires a modern front-end stack capable of delivering high performance and maintainability. The architectural plan recommends React with TypeScript, Next.js for server-side rendering, and a testing toolchain based on Jest and Playwright.

## Decision

Adopt **Next.js 14** with React 18 and TypeScript 5 as the baseline. Use Jest for unit tests, Playwright for end-to-end tests, and Storybook for UI development. This combination provides strong typing, fast builds and a rich ecosystem of tools.

While the original plan targeted Next.js 15, that version is still in prerelease and several key dependencies do not yet provide stable support. Until the ecosystem catches up, we pin the dashboard to the latest 14.x release for predictable builds and easier upgrades later.

## Consequences

All front-end code will follow the Feature-Sliced Design (FSD) structure. The toolchain will enforce linting and formatting via ESLint and Prettier. Future decisions around state management and data fetching libraries will extend this ADR.
