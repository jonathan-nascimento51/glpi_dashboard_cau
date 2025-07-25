# Project-specific bash configuration
# Ensures standard utilities are unaliased and available.

# Unalias common tools in case other environment managers define them
for cmd in ls grep sed awk; do
    unalias "$cmd" 2>/dev/null || true
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "WARNING: $cmd not found in PATH" >&2
    fi
done
