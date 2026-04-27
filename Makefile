# ─── Config ───────────────────────────────────────────
PYTHON  = .venv/bin/python
PIP     = .venv/bin/pip
RUFF    = .venv/bin/ruff

SO ?=
SO_REAL := $(shell uname -s | tr '[:upper:]' '[:lower:]' | sed 's/darwin/macos/;s/linux/debian/')

.PHONY: setup install lint format lint-fix check test test-cov clean run help

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
	@bash scripts/check_env.sh
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
