- `VITE_API_BASE_URL`: must point to `http://localhost:8000` when running under Docker Compose.
  The previous name `NEXT_PUBLIC_API_BASE_URL` is still accepted for legacy builds.
  You can also create `.env.local` with this setting for local scripts outside Docker.
- `DISALLOWED_PROXIES`: comma-separated list of proxy hosts ignored by `scripts/validate_credentials.py`.

## Shell configuration

A project `.bashrc` is provided at the repository root. Source this file after running `scripts/setup/setup_env.sh` to ensure standard utilities like `ls`, `grep`, `sed`, and `awk` are not aliased by tools such as `mise`:

```bash
source .bashrc
```

The script unaliases these commands and warns if any are missing from `$PATH`.
