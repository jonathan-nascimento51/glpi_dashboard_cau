# AsyncIO Validation Checks

This document outlines automated checks that help enforce our asyncio architecture principles.

## Goals

Detect common issues such as:

- Multiple event loops created in the same thread
- Misuse of `asyncio.run()` inside asynchronous functions
- Synchronous I/O inside `async def` blocks

## Implementation

We provide a simple AST-based script (`scripts/validate_asyncio.py`) that scans Python files and reports potential problems:

```bash
python scripts/validate_asyncio.py src/
```

### Checks performed

1. **Multiple loops** – flags more than one call to `asyncio.new_event_loop()` in a single file.
2. **Nested `asyncio.run`** – reports `asyncio.run()` calls found within coroutines.
3. **Synchronous libraries** – warns about usage of `requests` or `open()` inside `async def` functions.

These checks can be extended or integrated with tools like `flake8` or `pylint` using custom plugins.
