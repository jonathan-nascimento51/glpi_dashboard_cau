### Frontend Hot-Reload
- Mount local `./src/frontend/react_app` into `/app` for instant rebuild
- Preserve `node_modules` in `frontend_node_modules` volume to avoid being overwritten
- Expose Vite on 5173 with `--host 0.0.0.0`
