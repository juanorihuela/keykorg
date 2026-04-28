# Piezas Clave — Services

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
| `shell` | ejecuta `command` arbitrario; `wait: true` bloquea hasta que termine; `wait_threshold` (default 2s) dispara `wait.wav` en loop si el proceso tarda más |

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

`play_sound(filename)` permite reproducir cualquier sonido directamente (usado por `SequenceService` para `wait.wav`).

El reproductor de audio se detecta en `os_helpers.get_sound_player(volume)`. Orden de preferencia: `paplay` (soporta volumen), `afplay`, `aplay` (sin control de volumen por comando).

Archivos de sonido:
- Viven en `src/static/sounds/`
- La ruta se accede solo a través de `settings.sounds_dir`
- Si un archivo no existe, loguea warning y continúa sin crashear
- El volumen se controla desde `NotificationService(sounds_dir, volume=0.7)`
