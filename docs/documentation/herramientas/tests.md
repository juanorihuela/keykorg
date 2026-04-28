# Tests — Estructura y Convenciones

---

## Estructura

```
tests/
├── conftest.py          # Fixtures globales compartidas
├── __init__.py
└── unit/                # Tests unitarios por módulo
    ├── __init__.py
    ├── test_command_service.py
    ├── test_sequence_service.py
    ├── test_pad_handler.py
    ├── test_constants.py
    └── test_settings.py
```

---

## conftest.py — fixture global

```python
def make_pad_event(pad_id: int = 1, velocity: int = 100) -> PadEvent:
    return PadEvent(pad_id=pad_id, velocity=velocity, timestamp=datetime.now())
```

Usar `make_pad_event()` en cualquier test que necesite un `PadEvent`. No construir inline.

---

## Módulos con cobertura obligatoria

| Módulo | Qué se testea |
|---|---|
| `services/command_service.py` | happy path, FileNotFoundError, Exception genérica |
| `services/sequence_service.py` | orden de steps, errores por step, cada action type |
| `handlers/pad_handler.py` | pad sin mapear, type=simple, type=sequence, type desconocido |
| `config/constants.py` | valores de constantes críticas |
| `config/settings.py` | carga de .env, validaciones |

## Módulos excluidos de coverage

Dependen de hardware externo, del SO o son bootstrapping puro:

```toml
omit = [
    "src/core/midi_listener.py",
    "src/services/notification_service.py",
    "src/helpers/os_helpers.py",
    "src/main.py",
    "src/static/*",
    "src/config/log_config.py",
]
```

---

## Convenciones

- Un archivo de test por módulo: `test_<nombre>.py`
- Agrupar casos por método en clases: `class TestExecute`, `class TestRunStep`
- Usar `MagicMock` para inyectar dependencias (`NotificationService`, etc.)
- Parchear con `patch("ruta.del.modulo.bajo.test.Simbolo")` — no el origen, el destino
- Los tests no tocan disco, red ni hardware — todo se mockea o parchea
- Un test = un comportamiento, nombre descriptivo en snake_case

---

## Ejecutar tests

```bash
make test            # todos los tests, verbose
make test-cov        # tests + cobertura por línea

# un archivo específico
.venv/bin/python -m pytest tests/unit/test_command_service.py -v

# un test específico
.venv/bin/python -m pytest tests/unit/test_command_service.py::TestExecute::test_happy_path_returns_true -v
```

---

## Agregar tests a un módulo nuevo

1. Crear `tests/unit/test_<nombre>.py`
2. Inyectar dependencias con `MagicMock` como fixtures de pytest
3. Agrupar casos por método en clases `Test<Método>`
4. Si el módulo necesita un `PadEvent`, usar `make_pad_event()` de `conftest`
5. Verificar que `make test-cov` sigue pasando el umbral del 80%
