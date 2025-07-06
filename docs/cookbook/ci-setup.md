# CI Setup

## Context

The project relies on automated checks to keep the codebase healthy. Running
linters and tests on each commit helps avoid regressions and enforces a
consistent style across contributors. Continuous integration ensures each
change is evaluated in the same environment, reducing manual validation and
catching integration issues early.
## Decision

Use GitHub Actions to provide a repeatable CI pipeline. The workflow is named
`ci.yml` and lives in `.github/workflows/`. It runs automatically on every push
and pull request, allowing the project to test multiple Python versions through
a matrix build.
## Consequences

All contributions are validated in a clean environment before they reach the
main branch. Failing checks block a merge until the issues are fixed, providing
immediate feedback to contributors and keeping the repository stable.
## Steps

1. Create `.github/workflows/ci.yml` to store the pipeline definition.
2. Add a `checkout` step so the workflow can pull the repository contents.
3. Use `setup-python` to install the required Python version.
4. Install dependencies.
5. Run `pre-commit` to apply linting hooks.
6. Execute `pytest` to run the test suite.
