# CI Setup

## Context

The project relies on automated checks to keep the codebase healthy. Running
linters and tests on each commit helps avoid regressions and enforces a
consistent style across contributors.
## Decision

Use GitHub Actions to provide a repeatable CI pipeline. The workflow lives in
`.github/workflows/ci.yml` and is executed for every push and pull request.
## Consequences

All contributions are validated in a clean environment before they reach the
main branch. Failing checks block a merge until the issues are fixed.
## Steps

1. Create `.github/workflows/ci.yml`.
2. Configure the workflow with the following main steps:
   - `checkout` – pulls the repository contents.
   - `setup-python` – installs the desired Python version.
   - `pre-commit` – runs linting hooks.
   - `pytest` – executes the test suite.
