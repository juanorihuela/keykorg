# Logging — KeyKorg

---

## Sistema de archivos

- Directorio `logs/` en la raíz, generado en runtime
- Un archivo por día: `keykorg_YYYY-MM-DD.log`
- Formato de línea: `2026-04-26 14:32:01 | INFO  | COMPONENTE_EVENTO | key=value`
- Nivel configurable desde `.env` con `LOG_LEVEL`
- Retención configurada en `LOG_BACKUP_COUNT` (ver `src/config/constants.py`)
- Configurado en `LogConfig.setup()` antes de cualquier otra operación

---

## `config/log_config.py` — clase `LogConfig`

Configura el sistema de logging global con un solo método de clase: `LogConfig.setup(log_level)`.

Crea dos handlers: archivo rotativo diario y consola. Se llama una sola vez en `main.py` antes de cualquier `logger.info/error`.

---

## Convenciones en módulos

Cada módulo declara su propio logger al inicio:

```python
import logging
logger = logging.getLogger(__name__)
```

Reglas:
- Nunca llamar `logger.setLevel()` en los módulos — el nivel lo controla `LogConfig.setup()`
- Strings con nombre de pad siempre con `!r` para que aparezcan entre comillas en el log

Formato de mensajes:

```python
logger.info(f"EVENTO | pad_id={event.pad_id} | name={pad_name!r}")
logger.warning(f"EVENTO_WARN | ... | error={ex}")
logger.error(f"EVENTO_FAIL | error={type(ex).__name__}: {ex}")
```

---

## Catálogo de eventos

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
