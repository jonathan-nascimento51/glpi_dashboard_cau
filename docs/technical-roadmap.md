# Technical Roadmap 0-12 Months

```mermaid
gantt
    title Evolution Roadmap
    dateFormat  YYYY-MM
    section Phase A
    Monolith consolidation :a1, 2024-07, 3m
    section Phase B
    First microservice :b1, after a1, 3m
    section Phase C
    Test & Observability automation :c1, after b1, 3m
    section Phase D
    Event sourcing exploration :d1, after c1, 3m
```

| Phase | Goal | Exit Criteria |
|-------|------|---------------|
|A|Stabilize monolith with Clean Architecture|85% unit test coverage|
|B|Extract first service once backlog stabilizes|Service deployed with <5% error rate|
|C|Automate testing and monitoring|CI runtime <10m, dashboards active|
|D|Evaluate event sourcing or CQRS|ADR approved and prototype demo|
