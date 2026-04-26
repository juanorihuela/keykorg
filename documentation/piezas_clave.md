# Piezas Clave — KeyKorg

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
settings.commands_file  # Path absoluto a src/config/commands.{so}.yaml
settings.log_level      # nivel de logging (INFO, DEBUG, etc.)
settings.is_pending     # bool: True si el SO está en estado "pending"
settings.load_pad_map() # lee el YAML y devuelve el dict de pads
```

---

## `config/log_config.py` — clase `LogConfig`

Configura el sistema de logging global con un solo método de clase: `LogConfig.setup(log_level)`.

Crea dos handlers: archivo rotativo diario y consola. Se llama una sola vez en `main.py` antes de cualquier `logger.info/error`.

---

## `core/midi_listener.py` — clase `MidiListener`

Responsabilidad única: escuchar el dispositivo MIDI y emitir eventos.

- `wait_for_connection(device_name, retries, delay)` — método estático, intenta conectar N veces. Usado en `main.py` antes de instanciar el listener.
- `listen()` — bucle bloqueante. Por cada `note_on` con `velocity > 0` crea un `PadEvent` y llama al callback `on_pad_press`.
- `_resolve_device()` — busca el puerto real del dispositivo por substring del nombre.

No ejecuta ninguna lógica de negocio. Solo escucha y delega.

---

## `dtos/pad_event.py` — dataclass `PadEvent`

```python
@dataclass
class PadEvent:
    pad_id: int       # nota MIDI del pad presionado
    velocity: int     # intensidad del golpe
    timestamp: datetime
```

Viaja desde `MidiListener` hasta `PadHandler`. No tiene métodos ni lógica.

---

## `handlers/pad_handler.py` — clase `PadHandler`

Único punto que decide qué hacer con un pad presionado. Lee el `pad_map` y despacha a `CommandService` o `SequenceService` según el campo `type` del pad.

Después de ejecutar, notifica el resultado:
- éxito → `notify_done(pad_name)`
- error → `notify_alert(pad_name, "Error al ejecutar")`

Si el pad no tiene configuración en el YAML, loguea warning y no hace nada más.

---

## `services/command_service.py` — clase `CommandService`

Ejecuta un comando de shell simple con `subprocess.Popen`. Usa `shlex.split` para parsear el string del comando. No bloquea: el proceso hijo corre en background.

Captura `FileNotFoundError` (binario no encontrado) y cualquier otra excepción, loguea el error y retorna `False`.

---

## `services/sequence_service.py` — clase `SequenceService`

Ejecuta una lista de pasos en orden. Cada paso tiene un campo `action`:

| action | descripción |
|---|---|
| `open` | ejecuta `app` como comando de shell |
| `close_all` | cierra todas las ventanas (`wmctrl -k on`) |
| `notify` | muestra notificación de SO sin sonido |
| `delay` | espera N segundos (`seconds`) |
| `shell` | ejecuta `command` arbitrario |

Si un paso falla, la excepción sube y `execute()` retorna `False`.

---

## `services/notification_service.py` — clase `NotificationService`

Maneja notificaciones nativas de SO y reproducción de sonido. Los 4 tipos y su semántica:

| método | sonido | cuándo usarlo |
|---|---|---|
| `notify_success` | `success.wav` | Procesos importantes (ej: conexión MIDI establecida) |
| `notify_done` | `done.wav` | Acción completada correctamente (ej: pad ejecutado) |
| `notify_warning` | `warning.wav` | Alerta no crítica (ej: config faltante, elemento no encontrado) |
| `notify_alert` | `alert.wav` | Error crítico o excepción |

El reproductor de audio se detecta automáticamente en `os_helpers.get_sound_player()` (busca `aplay`, `paplay`, `afplay` en ese orden).

---

## `helpers/os_helpers.py`

Dos funciones:

- `get_host_so()` — detecta el SO anfitrión y lo mapea a una clave de `SO_CATALOG`. Usa `platform.system()`. Devuelve `None` si el SO no está en el mapa.
- `get_sound_player()` — devuelve el primer reproductor de audio disponible como lista de args para `subprocess.Popen`.

---

## `config/commands.{so}.yaml`

Define el comportamiento de cada pad. Estructura:

```yaml
pads:
  {pad_id: int}:
    name: str          # nombre descriptivo, aparece en logs y notificaciones
    type: simple | sequence
    command: str       # solo si type=simple
    steps: list        # solo si type=sequence
```

Los `pad_id` son las notas MIDI del dispositivo. Para el nanoPAD2, los pads van del 36 al 51.
