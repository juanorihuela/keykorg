# 05 — Pruebas unitarias con pytest

## Decisión de cobertura

Se testea lógica de negocio pura. Se excluyen I/O de dispositivos físicos, side effects de audio/OS, y detección trivial de SO — el costo de mockearlos supera el valor.

| Módulo | Prioridad | Motivo |
|---|---|---|
| `handlers/pad_handler.py` | Alta | Corazón del sistema, múltiples ramas |
| `config/settings.py` | Alta | Validaciones de arranque críticas |
| `config/constants.py` | Alta | Catálogo de SOs define comportamiento de arranque |
| `services/sequence_service.py` | Media | Ejecución ordenada con manejo de errores |
| `services/command_service.py` | Media | Dos ramas de error distintas |
| `core/midi_listener.py` | Omitir | I/O puro, requiere mock de dispositivo físico |
| `services/notification_service.py` | Omitir | Side effects de audio/OS, sin lógica testeable |
| `helpers/os_helpers.py` | Omitir | Detección trivial de SO, difícil de mockear bien |

---

## Configuración

### Dependencias

```
pytest
pytest-cov
```

### Estructura de directorios

```
tests/
  unit/
    test_pad_handler.py
    test_settings.py
    test_constants.py
    test_sequence_service.py
    test_command_service.py
  conftest.py
```

### Configuración de cobertura

Agregar en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
source = ["src"]
omit = [
    "src/core/midi_listener.py",
    "src/services/notification_service.py",
    "src/helpers/os_helpers.py",
    "src/main.py",
    "src/static/*",
    "src/config/log_config.py",
]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

Comando de ejecución:

```bash
pytest --cov --cov-report=term-missing
```

---

## Alta prioridad

### `PadHandler.handle()` — `tests/unit/test_pad_handler.py`

El handler recibe un `PadEvent` y hace dispatch. Los mocks reemplazas las tres dependencias de servicio.

**Fixture base:**
Crear un `PadHandler` con `command_service`, `sequence_service` y `notification_service` como `MagicMock`. El `pad_map` varía por test.

#### Pad no mapeado

- **happy path ausente**: `event.pad_id` no existe en `pad_map` → llama `notification_service.notify_warning` con mensaje que contiene el `pad_id`, no llama a ningún servicio de ejecución, no llama `notify_done`.

#### Tipo `simple`

- **happy path**: `pad_type="simple"`, `command_service.execute` retorna `True` → llama `command_service.execute(pad_config["command"], pad_name)`, llama `notify_done(pad_name, skip_notify=False, skip_sound=False)`.
- **ejecución falla**: `command_service.execute` retorna `False` → no llama `notify_done`.
- **skip_notify=True**: `notify_done` recibe `skip_notify=True`.
- **skip_sound=True**: `notify_done` recibe `skip_sound=True`.

#### Tipo `sequence`

- **happy path**: `pad_type="sequence"`, `sequence_service.execute` retorna `True` → llama `notification_service.notify_sequence()` antes del dispatch, luego llama `sequence_service.execute(steps, pad_name)`, luego llama `notify_done`.
- **ejecución falla**: `sequence_service.execute` retorna `False` → no llama `notify_done`, pero sí llamó `notify_sequence`.

#### Tipo desconocido

- `pad_type="foobar"` → llama `notification_service.notify_warning(pad_name, ...)`, retorna sin llamar `notify_done`, no llama a `command_service` ni `sequence_service`.

---

### `Settings` — `tests/unit/test_settings.py`

Las pruebas usan `tmp_path` de pytest para crear archivos `.env` reales y mockean `get_host_so`.

**Mock necesario:** parchear `config.settings.get_host_so` para controlar el SO anfitrión.

#### `_validate_so`

- **SO fuera del catálogo**: `Settings("windows")` → `ValueError` con mención del SO inválido y la lista de disponibles.
- **SO válido pero host distinto**: `get_host_so` retorna `"debian"`, se construye con `so="macos"` → `ValueError` indicando el mismatch.
- **SO válido, host coincide**: `get_host_so` retorna `"debian"`, `so="debian"` → no lanza excepción.
- **host desconocido (None)**: `get_host_so` retorna `None` → no lanza excepción para cualquier SO del catálogo.

#### `__init__` — carga de `.env`

- **archivo `.env` faltante**: SO válido, no existe `.env.{so}` → `FileNotFoundError`.
- **carga correcta**: `.env.debian` con `MIDI_DEVICE`, `SOUNDS_DIR`, `COMMANDS_FILE` → los atributos se asignan con los tipos correctos (`sounds_dir` y `commands_file` son `Path`).
- **LOG_LEVEL por defecto**: `.env` sin `LOG_LEVEL` → `settings.log_level == "INFO"`.
- **`is_pending` para SO activo**: SO `"debian"` → `settings.is_pending is False`.
- **`is_pending` para SO pendiente**: SO `"macos"` (con `get_host_so=None`) → `settings.is_pending is True`.

#### `load_pad_map`

- **archivo de comandos faltante**: `commands_file` apunta a ruta inexistente → `FileNotFoundError`.
- **YAML malformado**: archivo con contenido inválido → `ValueError` con mención de "YAML malformado".
- **sin imports**: YAML con sección `pads` directa → retorna el dict de pads.
- **con imports**: YAML con `imports: [a.yml, b.yml]` y los archivos importados con sus propias secciones `pads` → retorna merge de ambos dicts.
- **imports con claves solapadas**: si `a.yml` y `b.yml` definen el mismo pad, el último gana (comportamiento de `dict.update`).

---

### `SO_CATALOG` / arranque con SO pendiente — `tests/unit/test_constants.py`

- **catálogo contiene "debian" como activo**: `SO_CATALOG["debian"] == "active"`.
- **catálogo contiene "macos" como pendiente**: `SO_CATALOG["macos"] == "pending"`.
- **todos los valores son "active" o "pending"**: `all(v in {"active", "pending"} for v in SO_CATALOG.values())`.
- **`is_pending` aborta en `main`**: en `main.py`, cuando `settings.is_pending is True` se llama `sys.exit(1)`. Testear con mock de `Settings` que retorne `is_pending=True` y verificar `sys.exit` fue llamado con `1`.

---

## Media prioridad

### `SequenceService.execute()` — `tests/unit/test_sequence_service.py`

Mock necesario: `subprocess.Popen`, `subprocess.run`, `time.sleep`, `notification_service`.

#### Ejecución de pasos

- **lista vacía**: `execute([], "nombre")` → retorna `True`, no llama a ningún subprocess.
- **pasos en orden**: tres steps tipo `open` → `Popen` llamado tres veces en orden con los args correctos.
- **error en paso N**: el tercer step lanza `OSError` → retorna `False`, llama `notification_service.notify_alert(pad_name, ...)`, los pasos 1 y 2 ya se ejecutaron.

#### `_run_step` por acción

- **`action=open`**: llama `subprocess.Popen(shlex.split(app))`.
- **`action=delay`**: llama `time.sleep(seconds)` con el valor float del step.
- **`action=shell` sin `wait`**: llama `subprocess.Popen(shlex.split(command))`.
- **`action=shell` con `wait=True`**: llama `_run_blocking`, no `Popen` directamente.
- **`action=notify` con `sound`**: llama `notification_service.play_sound(sound)`.
- **`action=notify` con `message`**: llama `subprocess.Popen(["notify-send", message])`.
- **acción desconocida**: no lanza excepción, no llama a subprocess.

---

### `CommandService.execute()` — `tests/unit/test_command_service.py`

Mock necesario: `subprocess.Popen`, `notification_service`.

- **happy path**: `Popen` no lanza → retorna `True`, llama `Popen` con los tokens parseados del comando.
- **comando no encontrado (`FileNotFoundError`)**: `Popen` lanza `FileNotFoundError` → retorna `False`, llama `notification_service.notify_warning(pad_name, ...)`.
- **error genérico de ejecución**: `Popen` lanza `PermissionError` → retorna `False`, llama `notification_service.notify_alert(pad_name, ...)`.
- **comando vacío**: `command=""` → `Popen` llamado con lista vacía (sin crash en el servicio; el error viene del OS).

---

## Lo que no se testea y por qué

**`MidiListener`** — todo su valor está en la interacción con el dispositivo MIDI real. Un mock de `rtmidi` valida la plomería del wrapper, no el comportamiento. El riesgo es falsos positivos.

**`NotificationService`** — reproduce sonidos con `pygame` y lanza notificaciones del OS. Los tests serían mocks de mocks. El comportamiento observable es el side effect en sí.

**`os_helpers.get_host_so`** — una llamada a `platform.system()` con un `if/elif`. Mockear `platform` para verificar que el `if` funciona no aporta valor de regresión.
