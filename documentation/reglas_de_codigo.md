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
- Los comandos de los pads viven en `commands.{so}.yaml`, nunca hardcodeados en código

---

## Manejo de errores

- Cubrir la mayor cantidad de excepciones posible con manejo explícito
- Nunca usar `except Exception` como único handler sin loguear el tipo y mensaje
- Las excepciones de dominio propias van en `exceptions/`
- En los services, los errores se capturan, se loguean y se retorna `False` — no se relanza

---

## Logging

Formato obligatorio para todos los mensajes de log:

```
COMPONENTE_EVENTO | key=value | key=value
```

Ejemplos:
```
PAD_PRESS  | pad_id=37 | name='Chrome' | type=simple
CMD_OK     | name='Chrome' | command='google-chrome'
CMD_FAIL   | name='Postman' | command='...' | error=FileNotFoundError: ...
SEQ_OK     | name='Modo Dev'
SEQ_FAIL   | name='Modo Dev' | error=RuntimeError: ...
CONNECTION_FAIL | error=No se encuentra el dispositivo
GENERAL_ERROR   | error=TypeError: ...
```

Reglas:
- Usar `logger = logging.getLogger(__name__)` al inicio de cada módulo
- No llamar `logger.setLevel()` en los módulos — el nivel lo controla `LogConfig.setup()`
- Strings con nombre de pad siempre con `!r` para que aparezcan entre comillas en el log

---

## Notificaciones

Respetar la semántica de los 4 tipos. No usar `notify_success` para acciones rutinarias — eso es `notify_done`. `notify_success` queda reservado para eventos de sistema importantes.

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

- El campo `name` es obligatorio — aparece en logs y notificaciones
- El `pad_id` es la nota MIDI del dispositivo (entero)
- Los comandos `simple` usan strings completos que se parsean con `shlex.split`
- Las secuencias usan solo las acciones definidas: `open`, `close_all`, `notify`, `delay`, `shell`

---

## Archivos de sonido

- Viven en `src/static/sounds/`
- La ruta se accede solo a través de `settings.sounds_dir`
- Los 4 archivos esperados: `success.wav`, `done.wav`, `warning.wav`, `alert.wav`
- Si un archivo no existe, `notification_service` loguea warning y continúa sin crashear
