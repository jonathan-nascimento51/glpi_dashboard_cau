# ADR-0007: Refined Project Structure

Date: 2024-07-07

## Status

Proposed

## Context

As the codebase grew through multiple iterations and automated refactors, files became scattered across nested folders with outdated names. To ease onboarding and improve tooling, the project structure was re-evaluated and simplified. The new layout emphasises a clear separation of concerns between front-end, back-end and shared utilities.

## Decision

Adopt the directory layout summarised below. Each path is intended as a stable identifier so build scripts and documentation can reliably reference it.

## Consequences

* Facilitates code navigation and modular development.
* Provides predictable locations for configuration and tooling assets.
* Future migrations must preserve these paths or update scripts accordingly.

## Definição da Estrutura de Diretórios

| path | purpose |
| ---- | ------- |
| `/docker/` | Docker build contexts and compose files |
| `/docs/` | Architecture, ADRs and operational guides |
| `/examples/` | Minimal reproducible scripts and integration samples |
| `/githooks/` | Project-specific Git hooks |
| `/labs/` | Experimental notebooks and throwaway prototypes |
| `/resources/` | Static assets like images and SQL fixtures |
| `/scripts/` | Setup and maintenance utilities |
| `/src/` | Application source code |
| `/tests/` | Unit and integration tests |
