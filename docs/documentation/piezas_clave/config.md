# Piezas Clave — Configuración

---

## `config/constants.py`

Central de constantes del sistema. Cualquier valor literal que se use en más de un lugar vive aquí.

```python
SO_CATALOG          # dict con los SOs disponibles y su estado (active/pending)
CONNECTION_RETRIES  # intentos de conexión al dispositivo MIDI
CONNECTION_DELAY    # segundos entre cada intento
LOG_BACKUP_COUNT    # días de retención de logs
```

Regla: si agregás una constante nueva, va aquí. Nunca hardcodear valores en los módulos.

---

## `config/settings.py` — clase `Settings`

Único punto de acceso a toda la configuración del sistema. Se instancia en `main.py` con el SO objetivo.

Hace dos validaciones al inicializarse:
1. Que el SO exista en `SO_CATALOG`
2. Que el SO pedido coincida con el SO anfitrión real (detectado por `os_helpers.get_host_so()`)

Expone:
```python
settings.midi_device    # nombre del dispositivo MIDI (substring para buscar)
settings.sounds_dir     # Path absoluto a src/static/sounds/
settings.commands_file  # Path absoluto a src/config/commands/commands.{so}.yaml
settings.log_level      # nivel de logging (INFO, DEBUG, etc.)
settings.is_pending     # bool: True si el SO está en estado "pending"
settings.load_pad_map() # lee el YAML, resuelve paths y devuelve el dict de pads
```

`load_pad_map()` maneja dos excepciones explícitas:
- `FileNotFoundError` → mensaje claro si el archivo no existe
- `yaml.YAMLError` → mensaje claro si el YAML está malformado

Internamente, `_resolve_paths()` recorre todos los pads y resuelve el primer token de cada comando contra `PROJECT_ROOT`. Si el archivo existe, lo reemplaza con el path absoluto. Comandos como `"google-chrome"` no se modifican.

---

## `config/log_config.py` — clase `LogConfig`

Documentación completa en [config/logging.md](../config/logging.md).
