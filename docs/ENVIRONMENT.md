- `NEXT_PUBLIC_API_BASE_URL`: must point to `http://localhost:8000` when running under Docker Compose.
  You can also create `.env.local` with this setting for local scripts outside Docker.
- `DISALLOWED_PROXIES`: comma-separated list of proxy hosts ignored by `scripts/validate_credentials.py`.

- To avoid unexpected aliasing from `mise`, source `scripts/setup/unset_aliases.sh` or add its commands to your shell profile. This script unaliases core utilities (like `ls`, `grep`, `sed`, `awk`) and ensures `/usr/bin` and `/bin` are prioritized in your `$PATH`.
