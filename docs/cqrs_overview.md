# CQRS Overview

This project adopts a lightweight Command Query Responsibility Segregation (CQRS) pattern.
Write operations ingest raw tickets from GLPI into PostgreSQL while read operations serve
pre-computed views and cached metrics.

```text
@startuml
actor User
User -> Worker : commands (ingest tickets)
Worker -> PostgreSQL : write tickets
Worker --> Redis : cache metrics
Worker -> PostgreSQL : refresh mv_ticket_summary
User -> Dashboard : queries
Dashboard -> Worker : read from read model
Worker -> mv_ticket_summary : SELECT
@enduml
```

Commands are handled by the background workers. Queries never touch the write tables
directly and instead rely on the materialized view `mv_ticket_summary` or Redis caches.
This separation keeps analytical queries fast and isolated from ingestion workloads.
