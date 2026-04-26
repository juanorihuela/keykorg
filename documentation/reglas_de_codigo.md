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

Formato obligatorio para todos los mensajes de log:

```
COMPONENTE_EVENTO | key=value | key=value
```

Ejemplos:
```
PAD_PRESS       | pad_id=37 | name='Chrome' | type=simple
CMD_OK          | name='Chrome' | command='google-chrome'
CMD_NOT_FOUND   | name='Postman' | command='...' | error=...
CMD_FAIL        | name='App' | command='...' | error=TypeError: ...
SEQ_OK          | name='Modo Dev'
SEQ_FAIL        | name='Modo Dev' | error=RuntimeError: ...
PAD_UNMAPPED    | pad_id=45
CONNECTION_FAIL | error=No se encuentra el dispositivo
GENERAL_ERROR   | error=TypeError: ...
```

Reglas:
- Usar `logger = logging.getLogger(__name__)` al inicio de cada módulo
- No llamar `logger.setLevel()` en los módulos — el nivel lo controla `LogConfig.setup()`
- Strings con nombre de pad siempre con `!r` para que aparezcan entre comillas en el log

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

## YAML de comandos

- Los archivos reales van en `src/config/commands/` y están en `.gitignore`
- Los archivos `.example.yaml` son los templates versionados
- El campo `name` es obligatorio — aparece en logs y notificaciones
- El `pad_id` es la nota MIDI del dispositivo (entero)
- Los comandos `simple` usan strings completos parseados con `shlex.split`
- Los paths relativos en comandos se resuelven automáticamente contra `PROJECT_ROOT` en `Settings.load_pad_map()`
- Las secuencias usan solo las acciones definidas: `open`, `close_all`, `notify`, `delay`, `shell`

---

## Archivos de sonido

- Viven en `src/static/sounds/`
- La ruta se accede solo a través de `settings.sounds_dir`
- Los 5 archivos esperados: `success.wav`, `done.wav`, `warning.wav`, `alert.wav`, `bye.wav`
- Si un archivo no existe, `notification_service` loguea warning y continúa sin crashear
- El volumen se controla desde `NotificationService(sounds_dir, volume=0.7)`
