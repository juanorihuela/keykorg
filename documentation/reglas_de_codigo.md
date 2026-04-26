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

## YAML, scripts y sonidos

Reglas de configuración de archivos en [documentation/config/yaml_y_scripts.md](config/yaml_y_scripts.md).
