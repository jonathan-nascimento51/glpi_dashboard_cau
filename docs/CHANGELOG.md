- **src/frontend/react_app/Dockerfile**: upgraded base image from Node 18 to Node 20.19.0-alpine to fix `EBADENGINE` and crypto.hash errors.
- **tooling**: minimum frontend Node version is now **20.19**.
- **shared.dto**: `_validate_status` now accepts textual status values like `"closed"`.
