# Shared Utilities

This package hosts building blocks used across the backend and worker
applications. Modules under `shared` should be generic and independent
from any GLPI-specific business logic so they can be reused by other
projects.

## Available modules

- `dto.py` – simple data transfer objects and the `TicketTranslator` helper
  for converting raw GLPI payloads.
- `models/` – enums and dataclasses representing ticket information. These
  are also exported from `shared.models` for convenience.
- `resilience/` – retry and circuit breaker helpers for HTTP clients.
- `order_observer.py` – small example implementation of the observer pattern
  that logs events instead of printing them.

Importing from `shared` ensures a single definition is used everywhere
and avoids circular dependencies.
