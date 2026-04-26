# Guía para Modelos de IA — KeyKorg

Esta guía explica cómo leer el proyecto y cómo integrar cambios nuevos siguiendo los patrones existentes.

---

## Cómo leer el proyecto

El orden recomendado para entender el sistema:

1. `documentation/arquitectura.md` — visión general y flujo de datos
2. `documentation/piezas_clave.md` — qué hace cada clase
3. `documentation/reglas_de_codigo.md` — convenciones a respetar
4. `documentation/config/yaml_y_scripts.md` — configuración de pads, scripts y sonidos
5. `documentation/config/logging.md` — sistema de logs, formato y convenciones
6. `src/config/constants.py` — constantes del sistema
7. `src/config/settings.py` — cómo se carga la configuración
8. `src/main.py` — punto de entrada, flujo de arranque
9. `src/config/commands/commands.debian.example.yaml` — template raíz (imports)
10. `src/config/commands/debian/example/apps.example.yaml` — template de escenario

---

## Cómo integrar un cambio nuevo

### Agregar una acción nueva a secuencias

Editar solo `src/services/sequence_service.py`, método `_run_step`. Agregar el nuevo `elif`:

```python
elif action == "mi_accion":
    parametro = step.get("mi_parametro", "")
    # lógica aquí
```

No modificar `pad_handler.py` ni `command_service.py`.

---

### Agregar un SO nuevo

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

### Agregar un tipo de notificación nuevo

**Paso 1** — `src/services/notification_service.py`: agregar el método

```python
def notify_info(self, title: str, message: str = "") -> None:
    self._notify(title, message)
    self._play_sound("info.wav")
```

**Paso 2** — Agregar `src/static/sounds/info.wav`

**Paso 3** — Usar el nuevo método desde el componente que corresponda.

---

### Agregar una constante nueva

Siempre en `src/config/constants.py`. Importar desde ahí en el módulo que la necesite.

```python
# constants.py
MI_CONSTANTE = 42

# en el módulo que la usa
from config.constants import MI_CONSTANTE
```

---

### Agregar un servicio nuevo

1. Crear `src/services/mi_servicio.py` con una clase `MiServicio`
2. Si el servicio puede fallar, recibir `NotificationService` en el constructor y notificar desde adentro
3. Instanciar en `main.py` y pasar como dependencia al componente que lo necesite
4. No instanciar servicios dentro de otros servicios — la inyección ocurre en `main.py`

---

## Patrones obligatorios a seguir

### Logging en cada módulo

Ver [documentation/config/logging.md](config/logging.md) — convenciones, formato y catálogo de eventos.

### Manejo de errores en services

```python
def execute(self, ...) -> bool:
    try:
        # lógica
        logger.info(f"EVENTO_OK | ...")
        return True
    except EspecificException as ex:
        logger.warning(f"EVENTO_WARN | ... | error={ex}")
        self.notification_service.notify_warning(pad_name, "mensaje")
        return False
    except Exception as ex:
        logger.error(f"EVENTO_FAIL | ... | error={type(ex).__name__}: {ex}")
        self.notification_service.notify_alert(pad_name, "mensaje")
        return False
```

### Paths siempre desde `settings`

```python
# correcto
sound_path = self.sounds_dir / "archivo.wav"

# incorrecto — nunca hardcodear paths
sound_path = Path("src/static/sounds/archivo.wav")
```

---

## Qué NO hacer

- No usar `os.environ` directamente — siempre a través de `Settings`
- No agregar lógica de negocio en `main.py` — solo orquestación
- No agregar lógica en `midi_listener.py` — solo escucha y emite eventos
- No crear dependencias circulares entre capas
- No hardcodear el nombre del dispositivo MIDI — viene del `.env`
- No usar `notify_success` para acciones rutinarias — para eso existe `notify_done`
- No llamar `notify_alert` desde `PadHandler` en caso de fallo — el service ya lo hizo
- No crear archivos de más de 300 líneas
- No instanciar servicios dentro de otros servicios
- No versionar `commands.{so}.yaml` — son personales y van en `.gitignore`

---

## Verificación antes de integrar un cambio

1. ¿La clase nueva tiene una sola responsabilidad?
2. ¿Los paths usan `settings` como fuente de verdad?
3. ¿Los errores están capturados con mensaje descriptivo y notificación apropiada?
4. ¿El logging sigue el formato `EVENTO | key=value`?
5. ¿Las constantes nuevas están en `constants.py`?
6. ¿`main.py` sigue siendo solo orquestación?
7. ¿Los services nuevos reciben `NotificationService` si pueden fallar?
