### Frontend Hot-Reload
- Mount local `./src/frontend/react_app` into `/app` for instant rebuild
- Preserve `node_modules` in `frontend_node_modules` volume to avoid being overwritten
- Expose Vite on 5174 with `--host 0.0.0.0`

### Stabilizing React Hook Dependencies
React hooks such as `useEffect` compare dependency values by reference. Follow
these guidelines to avoid unnecessary re-renders:

- **Prefer primitives** – numbers, strings and booleans are stable by default.
- **Memoize objects** – create objects inside `useMemo` so React reuses the same
  reference:

  ```tsx
  const query = useMemo(() => ({ status }), [status])
  ```

- **Memoize callbacks** – wrap event handlers with `useCallback` when passing
  them down the component tree:

  ```tsx
  const handleClick = useCallback(() => fetchData(query), [fetchData, query])
  ```

- **Avoid `JSON.stringify`** – property order can change and functions are lost,
  causing unstable strings. Our `useApiQuery` hook uses a `stableStringify`
  helper instead. **Note**: it does not handle nested objects.

### Running tests
Install the runtime dependencies from `requirements.txt` **and** the development
set before running `pytest`. The optional extras in `requirements-dev.txt`
include `dash[testing]`, `playwright`, `fakeredis`, `testcontainers` and
`pact-python`.

```bash
pip install -r requirements-dev.txt --break-system-packages
```
This command installs the dev tools compiled via `pip-compile`. Make sure the
runtime dependencies are installed as well.
