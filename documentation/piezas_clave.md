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

- Pad no mapeado → `notify_warning` + return
- Tipo desconocido → `notify_warning` + return
- Éxito → `notify_done(pad_name)`
- Fallo → el service ya notificó, `PadHandler` no duplica la notificación

---

## `services/command_service.py` — clase `CommandService`

Recibe `NotificationService` en el constructor. Ejecuta un comando de shell simple con `subprocess.Popen`. Usa `shlex.split` para parsear el string del comando. No bloquea: el proceso hijo corre en background.

Manejo de errores propio:
- `FileNotFoundError` → `logger.warning` + `notify_warning` (binario no instalado, problema de config)
- `Exception` → `logger.error` + `notify_alert` (error inesperado)

---

## `services/sequence_service.py` — clase `SequenceService`

Recibe `NotificationService` en el constructor. Ejecuta una lista de pasos en orden. Cada paso tiene un campo `action`:

| action | descripción |
|---|---|
| `open` | ejecuta `app` como comando de shell |
| `close_all` | cierra todas las ventanas (`wmctrl -k on`) |
| `notify` | muestra notificación de SO sin sonido |
| `delay` | espera N segundos (`seconds`) |
| `shell` | ejecuta `command` arbitrario |

Si un paso falla, la excepción sube, `execute()` llama `notify_alert` y retorna `False`.

---

## `services/notification_service.py` — clase `NotificationService`

Maneja notificaciones nativas de SO y reproducción de sonido. Recibe `sounds_dir` y `volume` (default `0.7`) en el constructor.

Los 5 tipos y su semántica:

| método | sonido | cuándo usarlo |
|---|---|---|
| `notify_success` | `success.wav` | Procesos importantes del sistema (ej: conexión MIDI establecida) |
| `notify_done` | `done.wav` | Acción de pad completada correctamente |
| `notify_warning` | `warning.wav` | Alerta no crítica (cmd no encontrado, pad sin mapear, tipo desconocido) |
| `notify_alert` | `alert.wav` | Error crítico o excepción |
| `notify_bye` | `bye.wav` | Cierre del programa por KeyboardInterrupt |

El reproductor de audio se detecta en `os_helpers.get_sound_player(volume)`. Orden de preferencia: `paplay` (soporta volumen), `afplay`, `aplay` (sin control de volumen por comando).

---

## `helpers/os_helpers.py`

Dos funciones:

- `get_host_so()` — detecta el SO anfitrión y lo mapea a una clave de `SO_CATALOG`. Usa `platform.system()`. Devuelve `None` si el SO no está en el mapa.
- `get_sound_player(volume)` — devuelve el reproductor disponible con los flags de volumen correctos según el player.

---

## `config/commands/`

Contiene los YAMLs de mapeo de pads. Estructura de cada archivo:

```yaml
pads:
  {pad_id: int}:
    name: str          # nombre descriptivo, aparece en logs y notificaciones
    type: simple | sequence
    command: str       # solo si type=simple — parseado con shlex, paths resueltos automáticamente
    steps: list        # solo si type=sequence
```

Los archivos `*.example.yaml` son templates versionados. Los archivos reales (`commands.debian.yaml`, `commands.macos.yaml`) están en `.gitignore`.

Los `pad_id` son las notas MIDI del dispositivo. Para el nanoPAD2, los pads van del 36 al 51.
