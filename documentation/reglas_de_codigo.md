# Reglas de Código — KeyKorg

---

## Estructura

- Todo el código del programa vive dentro de `src/`
- Los archivos `.env.*` y `requirements.txt` van en la raíz del proyecto
- Ningún archivo `.py` debe superar las 300 líneas
- `main.py` es solo orquestación: sin lógica de negocio, sin funciones auxiliares sueltas

---

## Orientación a objetos

- Todo el código se organiza en clases con responsabilidades claras
- Una clase = una responsabilidad
- No crear funciones sueltas en módulos salvo en `helpers/` (utilidades puras sin estado)

---

## Configuración

- `Settings` es el único punto de acceso a valores de `.env`
- Nunca usar `os.environ` directamente fuera de `settings.py`
- Toda constante literal que se repita o tenga significado semántico va en `constants.py`
- Los comandos de los pads viven en `src/config/commands/commands.{so}.yaml`, nunca hardcodeados en código

---

## Manejo de errores

- Cubrir la mayor cantidad de excepciones posible con manejo explícito
- Nunca usar `except Exception` como único handler sin loguear el tipo y mensaje
- Las excepciones de dominio propias van en `exceptions/`
- Los services capturan sus propios errores, loguean, notifican y retornan `False` — no relanzan

---

## Notificaciones

Cada service es responsable de notificar sus propios fallos. `PadHandler` solo notifica el éxito. `main.py` notifica los errores del sistema (conexión, excepciones generales, cierre).

Semántica de los 5 tipos — no intercambiar:

| método | cuándo |
|---|---|
| `notify_success` | Eventos importantes del sistema (conexión MIDI establecida) |
| `notify_done` | Acción de pad completada |
| `notify_warning` | Alerta no crítica: cmd no encontrado, pad sin mapear, tipo desconocido |
| `notify_alert` | Error crítico: excepción inesperada, fallo de conexión |
| `notify_bye` | Cierre del programa (KeyboardInterrupt) |

`play_sound(filename)` es un método público para reproducir sonidos arbitrarios. Usado por `SequenceService` para `wait.wav` durante steps bloqueantes.

Sonido `wait.wav` — "procesando": se reproduce en loop mientras un step `shell` con `wait: true` sigue corriendo pasado el `wait_threshold`. Semánticamente distinto a los 5 tipos de notificación.

---

## Logging

Formato, catálogo de eventos y convenciones en [documentation/config/logging.md](config/logging.md).

---

## Imports

- Imports estándar primero, luego de terceros, luego locales
- Sin imports circulares: el flujo de dependencias es unidireccional
  ```
  main → config → helpers
  main → core → dtos
  main → handlers → services → helpers
  ```
- `helpers/` no importa nada del proyecto. `dtos/` tampoco.

---

## Lint y formato (Ruff)

El proyecto usa Ruff como único linter y formateador. Configuración en `pyproject.toml`.

- `make check` — verifica lint + formato sin modificar (usar en CI)
- `make lint-fix` — corrige automáticamente lo que puede Ruff
- El código debe pasar `make check` sin errores antes de integrar

Detalle de reglas activas y comandos en [herramientas/tooling.md](herramientas/tooling.md).

---

## Tests

- Los tests viven en `tests/unit/`, un archivo por módulo: `test_<nombre>.py`
- Los tests no tocan disco, red ni hardware — todo se mockea con `MagicMock` o `patch`
- Cobertura mínima: **80%** — `make test-cov` falla si no se alcanza
- Módulos que dependen de hardware o del SO están excluidos de coverage (ver [herramientas/tests.md](herramientas/tests.md))

---

## YAML, scripts y sonidos

Reglas de configuración de YAML en [config/yaml_comandos.md](config/yaml_comandos.md) y scripts en [config/scripts.md](config/scripts.md).
