# Piezas Clave — Core y DTOs

---

## `core/midi_listener.py` — clase `MidiListener`

Responsabilidad única: escuchar el dispositivo MIDI y emitir eventos.

- `wait_for_connection(device_name, retries, delay)` — método estático, intenta conectar N veces. Usado en `main.py` antes de instanciar el listener.
- `listen()` — bucle bloqueante. Por cada `note_on` con `velocity > 0` crea un `PadEvent` y llama al callback `on_pad_press`.
- `_resolve_device()` — busca el puerto real del dispositivo por substring del nombre.

No ejecuta ninguna lógica de negocio. Solo escucha y delega.

---

## `dtos/pad_event.py` — dataclass `PadEvent`

```python
@dataclass
class PadEvent:
    pad_id: int       # nota MIDI del pad presionado
    velocity: int     # intensidad del golpe
    timestamp: datetime
```

Viaja desde `MidiListener` hasta `PadHandler`. No tiene métodos ni lógica.
