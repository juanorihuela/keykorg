# Guía para Devs e IA — Patrones y Checklist

---

## Patrones obligatorios

### Logging en cada módulo

Ver [config/logging.md](../config/logging.md) — convenciones, formato y catálogo de eventos.

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
