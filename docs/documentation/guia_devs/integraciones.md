# Guía para Devs e IA — Integraciones

Cómo integrar cambios nuevos siguiendo los patrones existentes.

---

## Agregar una acción nueva a secuencias

Editar solo `src/services/sequence_service.py`, método `_run_step`. Agregar el nuevo `elif`:

```python
elif action == "mi_accion":
    parametro = step.get("mi_parametro", "")
    # lógica aquí
```

No modificar `pad_handler.py` ni `command_service.py`.

---

## Agregar un SO nuevo

**Paso 1** — `src/config/constants.py`: agregar al catálogo

```python
SO_CATALOG = {
    "debian": "active",
    "macos": "pending",
    "windows": "pending",  # nuevo
}
```

**Paso 2** — `src/helpers/os_helpers.py`: agregar la detección del SO anfitrión

```python
_HOST_SO_MAP = {
    "linux": "debian",
    "darwin": "macos",
    "windows": "windows",  # nuevo
}
```

**Paso 3** — Crear `.env.windows` en la raíz del proyecto

```env
SO=windows
MIDI_DEVICE=nanoPAD2
SOUNDS_DIR=src/static/sounds
COMMANDS_FILE=src/config/commands/commands.windows.yaml
LOG_LEVEL=INFO
```

**Paso 4** — Crear `src/config/commands/commands.windows.yaml` y `commands.windows.example.yaml`.

**Paso 5** — Agregar `src/config/commands/commands.windows.yaml` al `.gitignore`.

Cuando el SO esté listo para producción, cambiar su estado en `SO_CATALOG` de `"pending"` a `"active"`.

---

## Agregar un tipo de notificación nuevo

**Paso 1** — `src/services/notification_service.py`: agregar el método

```python
def notify_info(self, title: str, message: str = "") -> None:
    self._notify(title, message)
    self._play_sound("info.wav")
```

**Paso 2** — Agregar `src/static/sounds/info.wav`

**Paso 3** — Usar el nuevo método desde el componente que corresponda.

---

## Agregar una constante nueva

Siempre en `src/config/constants.py`. Importar desde ahí en el módulo que la necesite.

```python
# constants.py
MI_CONSTANTE = 42

# en el módulo que la usa
from config.constants import MI_CONSTANTE
```

---

## Agregar un servicio nuevo

1. Crear `src/services/mi_servicio.py` con una clase `MiServicio`
2. Si el servicio puede fallar, recibir `NotificationService` en el constructor y notificar desde adentro
3. Instanciar en `main.py` y pasar como dependencia al componente que lo necesite
4. No instanciar servicios dentro de otros servicios — la inyección ocurre en `main.py`
