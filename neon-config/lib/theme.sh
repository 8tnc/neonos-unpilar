NEON_VERSION="0.1.0"
NEON_HOME="${NEON_HOME:-/usr/local/share/neon}"

if [ -n "${NEON_FORCE_COLOR:-}" ] || { [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-dumb}" != "dumb" ]; }; then
    NEON_RED="$(printf '\033[31m')"
    NEON_RED_B="$(printf '\033[1;31m')"
    NEON_WHITE="$(printf '\033[1;37m')"
    NEON_GRAY="$(printf '\033[90m')"
    NEON_RESET="$(printf '\033[0m')"
else
    NEON_RED="" NEON_RED_B="" NEON_WHITE="" NEON_GRAY="" NEON_RESET=""
fi
