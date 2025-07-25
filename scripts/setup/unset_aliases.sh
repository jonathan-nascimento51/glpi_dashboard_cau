#!/usr/bin/env bash
# Ensure core utilities behave as expected when using mise or other env managers.
# Unalias common commands silently and prepend standard directories to PATH.
for cmd in ls grep sed awk; do
  unalias "$cmd" 2>/dev/null || true
done
export PATH="/usr/bin:/bin:$PATH"
