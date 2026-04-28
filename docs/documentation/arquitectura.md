# Arquitectura del Sistema — KeyKorg

## Descripción general

KeyKorg es un controlador MIDI por software. Escucha eventos de un dispositivo MIDI físico (nanoPAD2) y ejecuta comandos o secuencias de acciones en el sistema operativo según el pad presionado.

---

## Estructura de directorios

```
keykorg/
├── .env.debian                      # Config de entorno para distros Debian-based
├── .env.macos                       # Config de entorno para macOS (pending)
├── requirements.txt
├── pyproject.toml                   # Configuración de Ruff, pytest y coverage
├── Makefile                         # Comandos del proyecto (setup, lint, test, run…)
├── scripts/
│   ├── setup.sh                     # Crea .venv e instala deps
│   └── check_env.sh                 # Valida que el .env esté completo antes de `run`
├── tests/                           # Tests automáticos (pytest)
│   ├── conftest.py                  # Fixture global: make_pad_event()
│   └── unit/                        # Tests unitarios por módulo
│       └── test_*.py
├── documentation/                   # Esta carpeta
└── src/
    ├── main.py                      # Punto de entrada — solo orquestación
    ├── config/
    │   ├── constants.py             # Todas las constantes del sistema
    │   ├── log_config.py            # Clase LogConfig — setup de logging
    │   ├── settings.py              # Clase Settings — carga .env + validaciones
    │   └── commands/
    │       ├── commands.debian.yaml         # Raíz Debian — solo imports (gitignored)
    │       ├── commands.debian.example.yaml # Template raíz Debian (versionado)
    │       ├── commands.macos.yaml          # Raíz macOS — solo imports (gitignored)
    │       ├── commands.macos.example.yaml  # Template raíz macOS (versionado)
    │       ├── debian/
    │       │   ├── scene_1.yaml             # Apps, Sistema & Modos (gitignored)
    │       │   └── example/                 # Templates de referencia (versionados)
    │       │       ├── apps.example.yaml
    │       │       ├── dev.example.yaml
    │       │       └── misc.example.yaml
    │       └── macos/
    │           ├── *.yaml                   # Escenarios personales (gitignored)
    │           └── example/        # Templates de referencia (versionados)
    │               ├── apps.example.yaml
    │               └── dev.example.yaml
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
        │   ├── success.wav          # Procesos importantes del sistema
        │   ├── done.wav             # Acción de pad completada
        │   ├── warning.wav          # Alertas no críticas
        │   ├── alert.wav            # Errores críticos
        │   └── bye.wav              # Cierre del programa
        └── scripts/
            ├── examples/
            │   └── script.example.sh    # Template de referencia (versionado)
            └── *.sh                     # Scripts personales (gitignored)
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
.env.debian
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
    ├── pad no mapeado ──► notify_warning
    │
    ├── type=simple   ──► CommandService.execute()
    │                         ├── éxito:           notify_done
    │                         ├── cmd no encontrado: notify_warning
    │                         └── error:            notify_alert
    │
    └── type=sequence ──► SequenceService.execute()
                              ├── éxito:  notify_done
                              └── error:  notify_alert

KeyboardInterrupt ──► notify_bye
ConnectionFailed  ──► notify_alert
Exception general ──► notify_alert
```

---

## Configuración por SO

Cada SO tiene:
- Un archivo `.env.{so}` en la raíz del proyecto con rutas y parámetros del sistema
- Un archivo `src/config/commands/commands.{so}.yaml` con el mapeo de pads (gitignored)
- Un archivo `src/config/commands/commands.{so}.example.yaml` como template de referencia

`Settings` es el único punto de acceso a estos valores. Ningún otro módulo lee `.env` ni `os.environ` directamente.

El catálogo de SOs disponibles vive en `src/config/constants.py` (`SO_CATALOG`). Un SO puede estar en estado `"active"` o `"pending"`. Si está `"pending"`, el programa termina con error al arrancar.

