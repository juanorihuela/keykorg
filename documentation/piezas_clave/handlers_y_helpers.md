# Piezas Clave — Handlers y Helpers

---

## `handlers/pad_handler.py` — clase `PadHandler`

Único punto que decide qué hacer con un pad presionado. Lee el `pad_map` y despacha a `CommandService` o `SequenceService` según el campo `type` del pad.

- Pad no mapeado → `notify_warning` + return
- Tipo desconocido → `notify_warning` + return
- Éxito → `notify_done(pad_name)`
- Fallo → el service ya notificó, `PadHandler` no duplica la notificación

---

## `helpers/os_helpers.py`

Dos funciones:

- `get_host_so()` — detecta el SO anfitrión y lo mapea a una clave de `SO_CATALOG`. Usa `platform.system()`. Devuelve `None` si el SO no está en el mapa.
- `get_sound_player(volume)` — devuelve el reproductor disponible con los flags de volumen correctos según el player.

---

## `config/commands/`

Estructura y reglas de los archivos YAML de comandos en [config/yaml_comandos.md](../config/yaml_comandos.md).
