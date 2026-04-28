# KeyKorg v2 — Specs de Rediseño

## Objetivo

Rediseñar KeyKorg desde cero con una arquitectura robusta, multiplataforma y escalable.
La nueva versión debe soportar comandos simples y secuencias complejas por pad, con una
UX más pulida a nivel de notificaciones, logs y configuración.

---

## Arquitectura

- Todo el código debe estar orientado a objetos (clases y POO)
- Arquitectura dividida en capas con responsabilidades claras por directorio
- Ningún archivo debe superar las 300 líneas de código
- `main.py` debe ser lo más limpio posible: solo inicialización y punto de entrada
- Se deben cubrir la mayor cantidad de excepciones posibles con manejo explícito de errores

### Estructura de directorios (opcional)

```
keykorg/
├── main.py
├── .env.mint
├── .env.macos
├── config/
│   ├── settings.py             # Carga .env y commands.yaml según --so
│   ├── commands.mint.yaml      # Mapeo de pads para Linux Mint
│   └── commands.macos.yaml     # Mapeo de pads para macOS (pendiente)
├── core/
│   └── midi_listener.py        # Escucha y emite eventos MIDI
├── services/
│   ├── command_service.py      # Ejecuta comandos simples
│   ├── sequence_service.py     # Ejecuta secuencias de pasos
│   └── notification_service.py # Notificaciones de SO + sonido
├── handlers/
│   └── pad_handler.py          # Mapea pad_id → comando o secuencia
├── dtos/
│   └── pad_event.py            # Dataclass del evento de pad
├── helpers/
│   └── os_helpers.py           # Utilidades específicas por SO
├── static/
│   └── sounds/
│       ├── success.wav
│       └── alert.wav
└── logs/                       # Generado en runtime
```

---

## Configuración por SO

### Args de entrada

El script debe recibir un parse arg obligatorio `--so` al ejecutarse:

```bash
python main.py --so mint
python main.py --so macos
```

Catálogo de SOs disponibles — definido en `settings.py`:

```python
SO_CATALOG = {
    "mint": "active",
    "macos": "pending",  # TODO: integración pendiente
}
```

- Si el SO es `"pending"`, mostrar un warning claro en consola y en notificación de SO, pero no crashear
- Si el SO no existe en el catálogo, lanzar error con mensaje descriptivo y salir

### Archivos `.env` por SO

Cada SO tiene su propio `.env`. Solo contiene configuración del sistema, no comandos:

```env
# .env.mint
SO=mint
MIDI_DEVICE=KeyKorg
SOUNDS_DIR=static/sounds
COMMANDS_FILE=config/commands.mint.yaml
LOG_LEVEL=INFO
```

Todos los valores del `.env` deben ser accedidos de forma segura a través de `settings.py`,
nunca con `os.environ` directo en otros archivos.

---

## Comandos — YAML por SO

Los comandos y secuencias de cada pad se definen en el archivo `commands.{so}.yaml`.
El `.env` nunca contiene comandos.

### Tipos de pad

**Simple** — ejecuta un solo comando de sistema:

```yaml
pads:
  1:
    name: "Chrome"
    type: simple
    command: "xdg-open https://google.com"
```

**Sequence** — ejecuta una lista de pasos en orden:

```yaml
pads:
  5:
    name: "Modo Dev"
    type: sequence
    steps:
      - action: close_all
      - action: open
        app: terminal
      - action: open
        app: vscode
      - action: open
        app: spotify
      - action: notify
        message: "Modo Dev activado"
```

### Acciones disponibles en secuencias

| Acción | Descripción |
|---|---|
| `close_all` | Cierra todas las ventanas activas |
| `open` | Abre una app por nombre o comando |
| `notify` | Muestra una notificación de SO |
| `delay` | Espera N segundos antes del siguiente paso |
| `shell` | Ejecuta un comando de shell arbitrario |

---

## Logs

- Directorio `/logs` generado automáticamente en runtime
- Un archivo de log por día con formato: `keykorg_YYYY-MM-DD.log`
- Cada entrada debe incluir: timestamp, nivel, evento, pad_id, comando/secuencia, resultado
- Usar el módulo `logging` de Python con `RotatingFileHandler` o `TimedRotatingFileHandler`
- Nivel de log configurable desde `.env` con `LOG_LEVEL` (default INFO)

Ejemplo de entrada de log:

```
2025-01-15 14:32:01 | INFO  | PAD_PRESS  | pad_id=5 | name="Modo Dev" | type=sequence | status=success
2025-01-15 14:32:03 | ERROR | CMD_FAIL   | pad_id=1 | command="xdg-open ..." | error="FileNotFoundError"
```

---

## UX — Notificaciones

- Notificar al usuario con notificación nativa de SO en cada evento relevante
- Reproducir sonido junto con la notificación según el resultado:
  - Éxito → `static/sounds/success.wav`
  - Error → `static/sounds/alert.wav`

### Eventos que deben notificar

| Evento | Tipo | Mensaje sugerido |
|---|---|---|
| Conexión exitosa al dispositivo MIDI | success | "KeyKorg conectado ✓" |
| Fallo de conexión MIDI | alert | "No se pudo conectar a KeyKorg" |
| Comando ejecutado correctamente | success | Nombre del pad |
| Error al ejecutar comando | alert | Nombre del pad + descripción del error |
| SO pendiente de integración | alert | "SO {name} aún no está soportado" |

---

## Notas de implementación

- `pad_handler.py` es el único punto que decide si delegar a `command_service` o `sequence_service`
- `notification_service` es independiente y puede ser llamado desde cualquier capa
- Los sonidos `.wav` deben estar en `static/sounds/` y ser referenciados solo a través del valor del `.env`
- `dtos/pad_event.py` debe ser un `dataclass` con los campos: `pad_id`, `velocity`, `timestamp`
- `core/midi_listener.py` solo escucha y emite eventos — no ejecuta lógica de negocio