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
Install the runtime dependencies from `requirements.txt` **and** the base
development set before running `pytest`. Heavy packages used by the end-to-end
tests are listed separately in `requirements-full-tests.txt` and can also be
installed with `pip install -e '.[full-tests]'`.

```bash
pip install -r requirements-dev.txt -r requirements-full-tests.txt
# or
pip install -e '.[full-tests]'
```
**Note**: The `--break-system-packages` flag bypasses Python's external package management protection and can interfere with system packages. This flag is necessary for this project to ensure compatibility with certain development tools. However, it is strongly recommended to use a virtual environment to isolate dependencies and prevent interference with system-level Python packages. You can create and activate a virtual environment as follows:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt -r requirements-dev.txt
```

### SSL inspection and `pact-python`

Corporate proxies that inspect TLS traffic may cause `pip install pact-python` to fail with `CERTIFICATE_VERIFY_FAILED`. Provide the company's root certificate bundle and reuse it for Node scripts that invoke Pact:

```bash
export REQUESTS_CA_BUNDLE=/path/to/company-ca.pem
export NODE_EXTRA_CA_CERTS=$REQUESTS_CA_BUNDLE
pip install pact-python
```

Refer to the [Installing Dependencies Behind a Proxy or Offline](../README.md#installing-dependencies-behind-a-proxy-or-offline) section in the README for additional proxy configuration.
