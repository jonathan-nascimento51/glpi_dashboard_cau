# ADR-0003: API Versioning

Date: 2024-07-05

## Status

Proposed

## Context

The worker API is expected to evolve as new metrics are implemented and the GLPI
schema changes.  Front-end and external consumers need a stable contract to
avoid breaking with each release.

## Decision

Prefix all REST and GraphQL endpoints with a version number such as `/v1/`.
When breaking changes are required a new prefix (`/v2/`, `/v3/`…) will be
introduced while the previous version remains available for a deprecation
period.

## Consequences

* Clients can upgrade at their own pace by selecting the version they support.
* The project must maintain old routes while they are still in use, increasing
  maintenance overhead.

## Steps
