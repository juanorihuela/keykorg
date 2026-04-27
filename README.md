# KeyKorg

Controlador MIDI por software para Linux. Escucha eventos de un dispositivo MIDI físico (nanoPAD2 u otro) y ejecuta comandos o secuencias de acciones en el sistema operativo según el pad presionado.

---

## Requisitos

- Python 3.12
- Dispositivo MIDI conectado (USB o ALSA)
- Distro Debian-based (Ubuntu, Linux Mint, Pop!_OS…) — macOS en desarrollo

---

## Setup

```bash
make setup SO=debian
```

Crea el `.venv`, instala dependencias y copia `.env.debian.example` como `.env.debian`.

Editar `.env.debian` y completar `MIDI_DEVICE` con el nombre del dispositivo:

```bash
# listar dispositivos disponibles
aconnect -l
```

Crear el archivo de comandos a partir del template:

```bash
cp src/config/commands/commands.debian.example.yaml \
   src/config/commands/commands.debian.yaml
```

---

## Ejecutar

```bash
make run
```

Valida el `.env` y arranca la app. El proceso queda escuchando el dispositivo MIDI.
Salir con `Ctrl+C`.

---

## Desarrollo

```bash
make lint-fix    # corrige y formatea con Ruff
make check       # verifica lint + formato sin modificar (CI)
make test        # corre los tests con pytest
make test-cov    # tests + reporte de cobertura (umbral: 80%)
make clean       # elimina cachés y .pyc
```

Ver todos los comandos disponibles:

```bash
make help
```

---

## Documentación

[documentation/README.md](documentation/README.md) — índice completo de la documentación interna.
