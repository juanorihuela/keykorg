# Herramientas de Desarrollo

---

## Makefile — comandos disponibles

Todos los comandos asumen que el `.venv` ya fue creado con `make setup`.

| Comando | Qué hace |
|---|---|
| `make setup SO=debian` | Crea `.venv`, instala deps, copia `.env.<SO>` |
| `make install` | Solo actualiza dependencias desde `requirements.txt` |
| `make lint` | Revisa errores con Ruff sin modificar archivos |
| `make format` | Formatea el código con Ruff |
| `make lint-fix` | Corrige automáticamente + formatea |
| `make check` | Lint + formato sin modificar (modo CI) |
| `make test` | Corre todos los tests con pytest, verbose |
| `make test-cov` | Tests con reporte de cobertura por línea (`term-missing`) |
| `make run` | Valida `.env` y arranca la app |
| `make clean` | Elimina `__pycache__`, `.ruff_cache`, `.pytest_cache`, `.pyc` |

`SO` se autodetecta del sistema anfitrión si no se pasa explícitamente.

---

## pyproject.toml

Centraliza la configuración de Ruff, pytest y coverage. No hay `setup.cfg` ni `tox.ini`.

### Ruff — lint

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP", "C4", "SIM", "RUF", "N"]
```

| Código | Qué verifica |
|---|---|
| `E` / `W` | pycodestyle — errores y advertencias de estilo |
| `F` | Pyflakes — variables no usadas, imports fantasma |
| `I` | isort — ordenamiento de imports |
| `B` | bugbear — patrones que suelen esconder bugs |
| `UP` | pyupgrade — modernización a Python 3.12 |
| `C4` | comprehensions — listas y dicts verbosos |
| `SIM` | simplify — código innecesariamente complejo |
| `RUF` | reglas propias de Ruff |
| `N` | pep8-naming — convenciones de nombres |

### Ruff — formato

```toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

`pythonpath = ["src"]` permite importar módulos del proyecto sin prefijo en los tests:
```python
from services.command_service import CommandService  # correcto
```

### Coverage

```toml
[tool.coverage.report]
show_missing = true
fail_under = 80
```

Umbral mínimo: **80%**. Los módulos que dependen de hardware externo o del SO están excluidos
(ver [tests.md](tests.md) — sección "Módulos excluidos de coverage").

---

## Flujo de calidad en desarrollo

```
make lint-fix    # arregla lo que puede Ruff
make check       # falla si hay algo que corregir (para CI)
make test-cov    # falla si coverage < 80%
```
