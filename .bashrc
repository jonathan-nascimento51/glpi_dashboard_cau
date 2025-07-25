# Project-specific bash configuration
# Ensures standard utilities are unaliased and available.

# Unalias common tools in case other environment managers define them
for cmd in ls grep sed awk; do
    if [ "$(type -t "$cmd")" = "alias" ]; then
        unalias "$cmd"
    fi
    if ! command -v "$cmd" >/dev/null 2>&1; then
       echo "WARNING: $cmd not found in PATH" >&2
   fi
done
