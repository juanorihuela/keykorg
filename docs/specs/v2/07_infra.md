# 07 — Infraestructura: makefiles, scripts y deploy como servicio

## Objetivo

Agrupar todo el tooling (makefiles y scripts) bajo un directorio `infra/`, dejando únicamente un `Makefile` raíz que los importa. Separar las herramientas de desarrollo de las de deploy. Añadir soporte para instalar keykorg como **servicio de usuario** de `systemd` en Linux (Debian). macOS no soporta systemd; los comandos de deploy muestran un error claro.

---

## Estructura resultante

```
keykorg/
├── Makefile                    ← raíz: solo imports
├── pyproject.toml              ← debe tener [project] name = "keykorg"
└── infra/
    ├── dev.mk                  ← targets de desarrollo (lint, test, run…)
    ├── deploy.mk               ← targets de deploy (install, uninstall…)
    └── scripts/
        ├── setup.sh            ← (ya existe, se mueve aquí)
        ├── check_env.sh        ← (ya existe, se mueve aquí)
        ├── install.sh          ← nuevo
        └── uninstall.sh        ← nuevo
```

> **Prerrequisito:** `pyproject.toml` debe tener una sección `[project]` con `name = "keykorg"` para que `install.sh` pueda leer el nombre del servicio. Actualmente el archivo solo contiene configuración de herramientas (`[tool.*]`); hay que añadir la sección.

---

## Makefile raíz

Solo importa los sub-makefiles. No contiene lógica propia.

```makefile
include infra/dev.mk
include infra/deploy.mk
```

---

## infra/dev.mk

Contiene el contenido actual del `Makefile` sin modificaciones, con las rutas de scripts actualizadas a `infra/scripts/`.

```makefile
# ─── Config ───────────────────────────────────────────
PYTHON  = .venv/bin/python
PIP     = .venv/bin/pip
RUFF    = .venv/bin/ruff

SO ?=
SO_REAL := $(shell uname -s | tr '[:upper:]' '[:lower:]' | sed 's/darwin/macos/;s/linux/debian/')

.PHONY: setup install-deps lint format lint-fix check test test-cov clean run help

# ─── Setup ────────────────────────────────────────────
setup:           ## Crea el .venv, instala deps y copia .env.<SO>  (SO=debian|macos)
	@bash infra/scripts/setup.sh $(SO)

install-deps:    ## Solo instala/actualiza dependencias
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ─── Calidad de código ────────────────────────────────
lint:            ## Revisa errores con Ruff (sin modificar)
	$(RUFF) check .

format:          ## Formatea el código con Ruff
	$(RUFF) format .

lint-fix:        ## Corrige automáticamente lo que pueda Ruff
	$(RUFF) check . --fix
	$(RUFF) format .

check:           ## Verifica lint + formato sin modificar (modo CI)
	$(RUFF) check .
	$(RUFF) format . --check

# ─── Tests ────────────────────────────────────────────
test:            ## Corre los tests con pytest
	$(PYTHON) -m pytest tests/ -v

test-cov:        ## Tests con reporte de cobertura
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

# ─── Ejecución ────────────────────────────────────────
run:             ## Valida .env y arranca la app
	@bash infra/scripts/check_env.sh
	@set -a; . ./.env.$(SO_REAL); set +a; $(PYTHON) src/main.py --so $(SO_REAL)

# ─── Utilidades ───────────────────────────────────────
clean:           ## Elimina archivos temporales y caché
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

help:            ## Muestra este menú de ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
```

> `install` se renombra a `install-deps` para no colisionar con el target `install` de `deploy.mk`.

---

## infra/deploy.mk

Targets de ciclo de vida del servicio. Pasa `SO_REAL` a los scripts para que puedan reaccionar por plataforma. No requiere `sudo`.

```makefile
.PHONY: install uninstall reinstall status logs

install:         ## Instala keykorg como servicio de usuario (solo Linux)
	@bash infra/scripts/install.sh $(SO_REAL)

uninstall:       ## Detiene, deshabilita y elimina el servicio (solo Linux)
	@bash infra/scripts/uninstall.sh $(SO_REAL)

reinstall:       ## Desinstala y vuelve a instalar (útil al actualizar)
	@bash infra/scripts/uninstall.sh $(SO_REAL)
	@bash infra/scripts/install.sh $(SO_REAL)

status:          ## Muestra el estado del servicio
	@systemctl --user status keykorg

logs:            ## Sigue los logs del servicio en tiempo real
	@journalctl --user -u keykorg -f
```

---

## infra/scripts/install.sh

Seis pasos bien definidos. Sin `sudo` — es un servicio de usuario.

```bash
#!/usr/bin/env bash
set -euo pipefail

SO="${1:-}"

# ─── Paso 1: Nombre del servicio desde pyproject.toml ─
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SERVICE_NAME=$(grep -m1 '^name' "$PROJECT_DIR/pyproject.toml" \
    | sed 's/.*=\s*"\(.*\)"/\1/')

if [[ -z "$SERVICE_NAME" ]]; then
    echo "ERROR: no se encontró [project] name en pyproject.toml." >&2
    exit 1
fi

# ─── Paso 2: Validar SO ───────────────────────────────
if [[ "$SO" == "macos" ]]; then
    echo "ERROR: la instalación como servicio no está soportada en macOS." >&2
    echo "       En macOS usa 'make run' para arrancar la app manualmente." >&2
    exit 1
fi

if [[ "$SO" != "debian" ]]; then
    echo "ERROR: SO no reconocido ('$SO'). Valores válidos: debian | macos" >&2
    exit 1
fi

# ─── Paso 3: Validar systemctl --user ─────────────────
if ! command -v systemctl &>/dev/null; then
    echo "ERROR: systemctl no está disponible en este sistema." >&2
    exit 1
fi

SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/${SERVICE_NAME}.service"

# ─── Paso 4: Verificar .env.debian ────────────────────
ENV_FILE="$PROJECT_DIR/.env.debian"
ENV_EXAMPLE="$PROJECT_DIR/.env.debian.example"

if [[ ! -f "$ENV_FILE" ]]; then
    if [[ ! -f "$ENV_EXAMPLE" ]]; then
        echo "ERROR: no se encontró '$ENV_EXAMPLE'." >&2
        exit 1
    fi
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "==> Se copió $ENV_EXAMPLE → $ENV_FILE"
    echo "    Edita $ENV_FILE con tus valores y vuelve a correr: make install"
    exit 0
fi

# ─── Paso 5: Setup del entorno virtual ────────────────
echo "==> Ejecutando setup..."
if [[ -f "$PROJECT_DIR/infra/scripts/setup.sh" ]]; then
    bash "$PROJECT_DIR/infra/scripts/setup.sh" debian
else
    # fallback manual
    if [[ ! -d "$PROJECT_DIR/.venv" ]]; then
        python3 -m venv "$PROJECT_DIR/.venv"
    fi
    "$PROJECT_DIR/.venv/bin/pip" install \
        --upgrade pip -r "$PROJECT_DIR/requirements.txt"
fi

# ─── Paso 6: Generar y activar el .service ────────────
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
MAIN_PY="$PROJECT_DIR/src/main.py"

mkdir -p "$SERVICE_DIR"
echo "==> Generando $SERVICE_FILE..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=${SERVICE_NAME} MicroPad launcher
After=graphical.target

[Service]
Type=simple
ExecStart=${PYTHON_BIN} ${MAIN_PY}
Restart=always
Environment=DISPLAY=:0
Environment=XAUTHORITY=${HOME}/.Xauthority
WorkingDirectory=${PROJECT_DIR}

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME"
systemctl --user start  "$SERVICE_NAME"

echo "==> $SERVICE_NAME instalado y activo."
echo "    Estado: make status"
echo "    Logs:   make logs"
```

---

## infra/scripts/uninstall.sh

Limpio y quirúrgico: no toca código ni `.venv`. Sin `sudo`.

```bash
#!/usr/bin/env bash
set -euo pipefail

SO="${1:-}"

# ─── Validar SO ───────────────────────────────────────
if [[ "$SO" == "macos" ]]; then
    echo "ERROR: la desinstalación como servicio no está soportada en macOS." >&2
    exit 1
fi

if [[ "$SO" != "debian" ]]; then
    echo "ERROR: SO no reconocido ('$SO'). Valores válidos: debian | macos" >&2
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SERVICE_NAME=$(grep -m1 '^name' "$PROJECT_DIR/pyproject.toml" \
    | sed 's/.*=\s*"\(.*\)"/\1/')

if [[ -z "$SERVICE_NAME" ]]; then
    echo "ERROR: no se encontró [project] name en pyproject.toml." >&2
    exit 1
fi

SERVICE_FILE="$HOME/.config/systemd/user/${SERVICE_NAME}.service"

echo "==> Deteniendo $SERVICE_NAME..."
systemctl --user stop "$SERVICE_NAME" 2>/dev/null || true

echo "==> Deshabilitando $SERVICE_NAME..."
systemctl --user disable "$SERVICE_NAME" 2>/dev/null || true

if [[ -f "$SERVICE_FILE" ]]; then
    echo "==> Eliminando $SERVICE_FILE..."
    rm "$SERVICE_FILE"
fi

systemctl --user daemon-reload
echo "==> $SERVICE_NAME desinstalado."
```

---

## Ejemplo de .service generado

Se guarda en `~/.config/systemd/user/keykorg.service`.

```ini
[Unit]
Description=keykorg MicroPad launcher
After=graphical.target

[Service]
Type=simple
ExecStart=/home/rubiq/projects/apps/keykorg/.venv/bin/python /home/rubiq/projects/apps/keykorg/src/main.py
Restart=always
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/rubiq/.Xauthority
WorkingDirectory=/home/rubiq/projects/apps/keykorg

[Install]
WantedBy=default.target
```

---

## Flujos de trabajo

### Primera instalación (Linux)

```bash
make setup SO=debian    # crea .venv + .env.debian
# editar .env.debian si es necesario
make install            # genera el .service y lo activa
```

### Actualizar el proyecto (Linux)

```bash
git pull
make reinstall          # uninstall + install
```

### Desinstalar completamente (Linux)

```bash
make uninstall          # detiene, deshabilita y elimina el .service
                        # el código y .venv quedan intactos
```

### macOS

```bash
make setup SO=macos
make run                # arranque manual; install/uninstall muestran error
```

### Monitoreo

```bash
make status   # systemctl --user status keykorg
make logs     # journalctl --user -u keykorg -f
```

---

## Decisiones de diseño

- **`infra/` agrupa todo el tooling** para que la raíz del proyecto solo contenga código fuente, configuración y el `Makefile` de entrada. `scripts/` existente se mueve dentro de `infra/scripts/`.
- **`Makefile` raíz solo tiene `include`** — actúa como dispatcher. Esto mantiene los contextos separados y permite añadir más sub-makefiles sin tocar la raíz.
- **`install-deps` en vez de `install` en `dev.mk`** — evita la colisión de nombres con el `install` de `deploy.mk`.
- **Servicio de usuario (`~/.config/systemd/user/`) sin `sudo`** — al ser un servicio de usuario, systemd lo gestiona dentro de la sesión del usuario actual. No se necesitan privilegios de root, no hay riesgo de que los archivos del `.venv` queden con permisos de root, y el `.service` no aparece en el listado global del sistema.
- **`SO_REAL` se pasa como argumento a los scripts** — consistente con el patrón de `setup.sh`. Los scripts no deducen el SO internamente para que sean más fáciles de testear y más explícitos.
- **macOS falla con mensaje claro** — systemd no existe en macOS. La alternativa sería `launchd` (`.plist` en `~/Library/LaunchAgents/`), pero queda fuera del alcance de esta spec. El error guía al usuario a usar `make run`.
- **`install.sh` sale en el paso 4** si no existe `.env.debian` — obliga a revisar la configuración antes de que el servicio arranque. Más seguro que arrancar con valores vacíos o del ejemplo.
- **`uninstall.sh` no toca código ni `.venv`** — la desinstalación solo afecta la integración con systemd. El código lo gestiona git; el `.venv` se reutiliza en la siguiente instalación.
- **`systemctl --user daemon-reload` en ambos scripts** — garantiza que systemd refleje el estado real tras crear o eliminar un `.service`.
