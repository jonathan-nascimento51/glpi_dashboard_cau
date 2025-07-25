#!/usr/bin/env bash
# Ensure core utilities behave as expected when using mise or other env managers.
# Unalias common commands silently and prepend standard directories to PATH.
for cmd in ls grep sed awk; do
  unalias "$cmd" 2>/dev/null || true
done
for dir in /usr/bin /bin; do
  case ":$PATH:" in
    *":$dir:"*) ;; # Directory already in PATH, do nothing
    *) PATH="$PATH:$dir" ;; # Append directory to PATH
  esac
done
export PATH
