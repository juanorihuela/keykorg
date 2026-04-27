#!/usr/bin/env bash
set -euo pipefail

SO="${1:-}"

# ─── Validación del SO ────────────────────────────────
if [[ "$SO" != "debian" && "$SO" != "macos" ]]; then
    echo "ERROR: debes indicar el SO. Uso: make setup SO=debian|macos" >&2
    exit 1
fi

# ─── Detección del SO real ────────────────────────────
case "$(uname -s)" in
    Darwin) SO_REAL="macos"  ;;
    Linux)  SO_REAL="debian" ;;
    *)
        echo "ERROR: sistema operativo no soportado ($(uname -s))." >&2
        exit 1
        ;;
esac

if [[ "$SO" != "$SO_REAL" ]]; then
    echo "ERROR: indicaste SO=$SO pero este sistema es '$SO_REAL'." >&2
    exit 1
fi

ENV_EXAMPLE=".env.${SO}.example"
ENV_FILE=".env.${SO}"

# ─── Entorno virtual ──────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "==> Creando entorno virtual..."
    python3 -m venv .venv
fi

# ─── Dependencias ─────────────────────────────────────
echo "==> Instalando dependencias..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# ─── Archivo .env ─────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "ERROR: no se encontró '$ENV_EXAMPLE'." >&2
        exit 1
    fi
    echo "==> Copiando $ENV_EXAMPLE → $ENV_FILE"
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "    Edita $ENV_FILE con tus valores antes de correr la app."
else
    echo "==> $ENV_FILE ya existe, no se sobreescribe."
fi

echo "==> Setup completado para SO=$SO."
