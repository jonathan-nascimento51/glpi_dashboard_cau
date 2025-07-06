# ADR-0004: Cache Strategy

Date: 2024-07-05

## Status

Proposed

## Context

Metrics queries hit the GLPI API frequently and some calculations are expensive
to recompute.  The system already uses Redis but the policy for cache keys and
expiration times was not documented.

## Decision

Store all aggregated ticket data in Redis with explicit TTLs.  Endpoints such as
`/metrics/aggregated` expire after one hour, while daily summaries keep data for
24 hours.  The worker updates Redis after fetching from GLPI and persists the
results to PostgreSQL for long‑term storage.

## Consequences

* Significantly reduces load on the GLPI API and improves dashboard response
  times.
* Requires careful cache invalidation logic and monitoring of Redis memory
  usage.

## Steps
