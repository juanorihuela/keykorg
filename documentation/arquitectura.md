# Arquitectura del Sistema — KeyKorg

## Descripción general

KeyKorg es un controlador MIDI por software. Escucha eventos de un dispositivo MIDI físico (nanoPAD2) y ejecuta comandos o secuencias de acciones en el sistema operativo según el pad presionado.

---

## Estructura de directorios

```
keykorg/
├── .env.mint                        # Config de entorno para Linux Mint
├── .env.macos                       # Config de entorno para macOS (pending)
├── requirements.txt
├── explicacion.md                   # Flujo paso a paso del programa
├── documentacion/                   # Esta carpeta
└── src/
    ├── main.py                      # Punto de entrada — solo orquestación
    ├── config/
    │   ├── constants.py             # Todas las constantes del sistema
    │   ├── log_config.py            # Clase LogConfig — setup de logging
    │   ├── settings.py              # Clase Settings — carga .env + validaciones
    │   ├── commands.mint.yaml       # Mapeo de pads para Linux Mint
    │   └── commands.macos.yaml      # Mapeo de pads para macOS (placeholder)
    ├── core/
    │   └── midi_listener.py         # Escucha el dispositivo MIDI, emite PadEvents
    ├── dtos/
    │   └── pad_event.py             # Dataclass: pad_id, velocity, timestamp
    ├── services/
    │   ├── command_service.py       # Ejecuta comandos simples (type: simple)
    │   ├── sequence_service.py      # Ejecuta secuencias de pasos (type: sequence)
    │   └── notification_service.py  # Notificaciones de SO + sonido
    ├── handlers/
    │   └── pad_handler.py           # Único punto de dispatch: simple vs sequence
    ├── helpers/
    │   └── os_helpers.py            # Detección de SO anfitrión, reproductor de audio
    ├── exceptions/
    │   └── connection_failed.py     # Excepción de conexión MIDI fallida
    └── static/
        ├── sounds/
        │   ├── success.wav
        │   ├── done.wav
        │   ├── warning.wav
        │   └── alert.wav
        └── scripts/
            ├── code_here.sh
            └── react_localhost.sh
```

---

## Capas y responsabilidades

```
┌─────────────────────────────────────────────────┐
│                    main.py                      │  Orquestación pura
├─────────────────────────────────────────────────┤
│                config/                          │  Configuración y arranque
│   constants.py  │  settings.py  │  log_config   │
├─────────────────────────────────────────────────┤
│                  core/                          │  Input MIDI
│              midi_listener.py                   │
├─────────────────────────────────────────────────┤
│                handlers/                        │  Decisión de negocio
│              pad_handler.py                     │
├─────────────────────────────────────────────────┤
│                services/                        │  Ejecución
│  command_service │ sequence_service │ notif...  │
├─────────────────────────────────────────────────┤
│           dtos/  │  helpers/  │  exceptions/    │  Soporte
└─────────────────────────────────────────────────┘
```

---

## Flujo de datos

```
.env.mint
    │
    ▼
Settings ──► LogConfig.setup()
    │
    ▼
MidiListener.wait_for_connection()
    │
    ▼
MidiListener.listen()  ◄──── bucle infinito
    │
    │  PadEvent(pad_id, velocity, timestamp)
    ▼
PadHandler.handle()
    │
    ├── type=simple   ──► CommandService.execute()
    └── type=sequence ──► SequenceService.execute()
                                │
                         éxito: notify_done()
                         error:  notify_alert()
```

---

## Configuración por SO

Cada SO tiene:
- Un archivo `.env.{so}` en la raíz del proyecto con rutas y parámetros del sistema
- Un archivo `src/config/commands.{so}.yaml` con el mapeo de pads

`Settings` es el único punto de acceso a estos valores. Ningún otro módulo lee `.env` ni `os.environ` directamente.

El catálogo de SOs disponibles vive en `src/config/constants.py` (`SO_CATALOG`). Un SO puede estar en estado `"active"` o `"pending"`. Si está `"pending"`, el programa termina con error al arrancar.

---

## Logging

- Directorio `logs/` en la raíz, generado en runtime
- Un archivo por día: `keykorg_YYYY-MM-DD.log`
- Formato: `2026-04-26 14:32:01 | INFO  | COMPONENTE_EVENTO | key=value`
- Nivel configurable desde `.env` con `LOG_LEVEL`
- Configurado en `LogConfig.setup()` antes de cualquier otra operación
