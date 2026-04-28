# 06 — Makefiles y scripts de configuración

## Objetivo

Centralizar la configuración, instalación y tareas de desarrollo del proyecto mediante una combinación de `Makefile` y scripts `.sh`. El `Makefile` actúa como punto de entrada único; los scripts resuelven la lógica de setup que no es idiomática en Make.

El proyecto soporta dos sistemas operativos: **Debian/Ubuntu** y **macOS**. El SO se pasa como variable al momento de correr `make setup`.

---

## Estructura de archivos

```
keykorg/
├── Makefile
├── .env.debian.example
├── .env.macos.example
└── scripts/
    ├── setup.sh          # Crea .venv, copia .env.<SO>, instala deps
    └── check_env.sh      # Valida que las vars de entorno requeridas existan
```

### Archivos .env por SO

Cada SO tiene su propio archivo de ejemplo porque pueden diferir en rutas, herramientas del sistema o variables específicas de plataforma:

| Archivo | Propósito |
|---|---|
| `.env.debian.example` | Template para entornos Debian/Ubuntu |
| `.env.macos.example` | Template para entornos macOS |
| `.env.debian` | Archivo activo en Debian (git-ignorado) |
| `.env.macos` | Archivo activo en macOS (git-ignorado) |

---

## scripts/setup.sh

Responsabilidades:
1. Validar que el parámetro `SO` sea `debian` o `macos`.
2. Crear el entorno virtual `.venv` si no existe.
3. Copiar `.env.<SO>.example` → `.env.<SO>` si no existe aún.
4. Instalar dependencias con `pip`.

```bash
#!/usr/bin/env bash
set -euo pipefail

SO="${1:-}"

# ─── Validación del SO ────────────────────────────────
if [[ "$SO" != "debian" && "$SO" != "macos" ]]; then
    echo "ERROR: debes indicar el SO. Uso: make setup SO=debian|macos" >&2
    exit 1
fi

ENV_EXAMPLE=".env.${SO}.example"
ENV_FILE=".env.${SO}"

# ─── Entorno virtual ──────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "==> Creando entorno virtual..."
    python -m venv .venv
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
```

---

## scripts/check_env.sh

Valida que las variables críticas estén definidas antes de ejecutar la app o los tests. Se puede llamar desde `make run` o `make test`.

```bash
#!/usr/bin/env bash
set -euo pipefail

REQUIRED_VARS=(DB_URL SECRET_KEY)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "ERROR: la variable de entorno '$var' no está definida." >&2
        exit 1
    fi
done
```

---

## Makefile

### Variables de configuración

```makefile
PYTHON  = .venv/bin/python
PIP     = .venv/bin/pip
RUFF    = .venv/bin/ruff

# SO debe pasarse como parámetro: make setup SO=debian|macos
SO ?=
```

### Targets

| Target | Descripción |
|---|---|
| `setup SO=debian\|macos` | Valida SO, crea `.venv`, copia `.env.<SO>` e instala deps |
| `install` | Solo instala/actualiza dependencias |
| `lint` | `ruff check .` — reporta errores sin modificar |
| `format` | `ruff format .` — formatea el código |
| `fix` | `ruff check . --fix` + `ruff format .` — corrige automáticamente |
| `check` | `ruff check .` + `ruff format . --check` — modo CI, sin modificar |
| `test` | `pytest tests/ -v` |
| `test-cov` | pytest con reporte de cobertura por terminal |
| `clean` | Elimina `__pycache__`, `.ruff_cache`, `.pytest_cache`, `*.pyc` |
| `run` | Valida vars de entorno y arranca la app |
| `help` | Lista todos los targets con su descripción |

### Makefile completo

```makefile
# ─── Config ───────────────────────────────────────────
PYTHON  = .venv/bin/python
PIP     = .venv/bin/pip
RUFF    = .venv/bin/ruff

SO ?=

.PHONY: setup install lint format fix check test test-cov clean run help

# ─── Setup ────────────────────────────────────────────
setup:           ## Crea el .venv, instala deps y copia .env.<SO>  (SO=debian|macos)
	@bash scripts/setup.sh $(SO)

install:         ## Solo instala/actualiza dependencias
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ─── Calidad de código ────────────────────────────────
lint:            ## Revisa errores con Ruff (sin modificar)
	$(RUFF) check .

format:          ## Formatea el código con Ruff
	$(RUFF) format .

fix:             ## Corrige automáticamente lo que pueda Ruff
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
	@bash scripts/check_env.sh
	$(PYTHON) -m src.main

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

---

## Flujos de trabajo típicos

### Primera vez en el proyecto (Debian)
```bash
make setup SO=debian
# editar .env.debian si es necesario
make run
```

### Primera vez en el proyecto (macOS)
```bash
make setup SO=macos
# editar .env.macos si es necesario
make run
```

### Ciclo de desarrollo diario
```bash
make fix      # formatea y corrige lint
make test     # corre los tests
```

### Antes de hacer push / en CI
```bash
make check    # lint + format sin modificar (falla si hay problemas)
make test-cov # tests con cobertura
```

---

## Decisiones de diseño

- **`SO` se valida en `setup.sh`**, no en el Makefile: Make no tiene manejo de errores idiomático; bash sí.
- **Un `.env` por SO** en lugar de uno compartido: las rutas, comandos del sistema y configuraciones pueden diferir entre plataformas.
- **`setup.sh` no sobreescribe** un `.env.<SO>` existente para no pisar configuración local ya editada.
- **`check` vs `fix`**: `check` es read-only y apropiado para CI; `fix` es para desarrollo local.
- **`test-cov` apunta a `--cov=src`** para medir solo el código del proyecto, no los tests ni scripts.
- **`check_env.sh` en `make run`** evita errores crípticos en runtime por variables faltantes.
