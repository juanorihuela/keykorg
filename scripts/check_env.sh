#!/usr/bin/env bash
set -euo pipefail

case "$(uname -s)" in
    Darwin) SO_REAL="macos"  ;;
    Linux)  SO_REAL="debian" ;;
    *)
        echo "ERROR: sistema operativo no soportado ($(uname -s))." >&2
        exit 1
        ;;
esac

ENV_FILE=".env.${SO_REAL}"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: no se encontró '$ENV_FILE'. Corre: make setup SO=$SO_REAL" >&2
    exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

REQUIRED_VARS=(SO MIDI_DEVICE SOUNDS_DIR COMMANDS_FILE LOG_LEVEL)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "ERROR: '$var' no está definida en $ENV_FILE." >&2
        exit 1
    fi
done
