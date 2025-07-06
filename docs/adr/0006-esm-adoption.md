# 0006. Adoption of ES Modules

Date: 2024-07-06

## Status

Accepted

## Context

Node.js now fully supports ES Modules (ESM). To ensure consistency across the
front-end and automation scripts, the project transitions from CommonJS to
native ESM. This simplifies imports and aligns with modern tooling.

## Decision

All JavaScript configuration and utility files should use ESM syntax. Files that
still rely on `module.exports` must use a `.cjs` extension. The `package.json`
includes `"type": "module"` so `.js` defaults to ESM. Scripts were updated to
use `import`/`export` and legacy configs were renamed to `.cjs`.

## Consequences

Developers must structure new Node files using ESM. When interoperating with
CommonJS modules, use the `.cjs` extension. Build tools like Vite and PostCSS
now load configuration via ESM.
