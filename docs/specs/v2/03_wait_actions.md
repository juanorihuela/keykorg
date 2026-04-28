# KeyKorg — Spec: Sequence Service — Pasos bloqueantes + Wait Notification

## Contexto

Actualmente `sequence_service.py` usa `subprocess.Popen` para ejecutar steps, lo que es
no bloqueante. Esto causa dos problemas:

1. La secuencia avanza sin esperar a que el paso anterior termine
2. No hay feedback visual/sonoro cuando un proceso tarda más de lo esperado

## Cambios requeridos

### `src/services/sequence_service.py`

Agregar soporte para el campo opcional `wait` en cada step del YAML.
Cuando `wait: true`, el step es bloqueante y activa el mecanismo de wait notification.

**Nuevos campos en el step del YAML:**

```yaml
- action: shell
  command: "python src/static/scripts/end_of_day.py"
  wait: true          # bloquea hasta que el proceso termine
  wait_threshold: 2   # segundos antes de disparar wait.wav (default: 2)
```

**Método `_run_step`** — detectar el campo `wait` y delegar:

```python
def _run_step(self, step: dict) -> None:
    action = step.get("action")
    wait = step.get("wait", False)
    threshold = step.get("wait_threshold", 2)

    if action == "shell":
        command = step.get("command", "")
        if wait:
            self._run_blocking(command, threshold)
        else:
            subprocess.Popen(shlex.split(command))

    # resto de actions sin cambios...
```

**Método `_run_blocking`** — ejecuta el proceso y dispara wait.wav si tarda:

```python
def _run_blocking(self, command: str, threshold: int) -> None:
    proc = subprocess.Popen(shlex.split(command))

    try:
        proc.wait(timeout=threshold)
        return  # terminó antes del threshold, sin wait.wav
    except subprocess.TimeoutExpired:
        pass  # tardó más, activar wait loop

    wait_thread = threading.Thread(
        target=self._play_wait_loop,
        args=(proc,),
        daemon=True
    )
    wait_thread.start()
    proc.wait()  # bloquea hasta que el proceso principal termine

def _play_wait_loop(self, proc: subprocess.Popen) -> None:
    while proc.poll() is None:  # mientras el proceso siga corriendo
        self.notification_service.play_sound("wait.wav")
        time.sleep(3)  # intervalo entre repeticiones
```

**Imports adicionales requeridos:**

```python
import threading
```

---

### `src/services/notification_service.py`

El método `_play_sound` actualmente es privado. Exponerlo como público para que
`sequence_service` pueda llamarlo directamente sin pasar por un `notify_*`:

```python
# cambiar de:
def _play_sound(self, filename: str) -> None:

# a:
def play_sound(self, filename: str) -> None:
```

Actualizar todas las llamadas internas de `_play_sound` a `play_sound`.
*Ya existe un método play_sound() publico*

---

### `src/static/sounds/`

Agregar `wait.wav` — sonido corto y neutro que indique "procesando". Diferente
semánticamente a los 5 existentes (`success`, `done`, `warning`, `alert`, `bye`).
*ya está el wav file en el directorio, no sustituir el file 'wait.wav' actual*

Actualizar `reglas_de_codigo.md` y `piezas_clave.md` para documentar el nuevo sonido.
También actualizar documentation/config/yaml_y_scripts.md con el nuevo campo 'wait' y 'wait_threshold'

---

## Comportamiento esperado

```
Pad presionado
    → step con wait: false  → Popen, no bloqueante, continúa inmediato
    → step con wait: true   → Popen bloqueante
                                → proceso termina antes de threshold → continúa sin sonido
                                → proceso tarda más de threshold    → wait.wav en loop
                                                                    → proceso termina
                                                                    → loop se detiene
                                                                    → siguiente step
```

---

## Reglas

- `wait` es opt-in por step — default `false`. Los steps sin `wait` no cambian su comportamiento
- Solo aplica a `action: shell` por ahora. `action: open` sigue siendo no bloqueante
- `wait_threshold` default: `2` segundos
- El loop de `wait.wav` se ejecuta en un thread daemon — no bloquea el proceso principal
- Cuando el proceso termina, el loop se detiene solo via `proc.poll()`

---

## Archivos a modificar

```
src/services/sequence_service.py        # _run_step, _run_blocking, _play_wait_loop
src/services/notification_service.py   # _play_sound → play_sound
```

## Archivos nuevos

```
src/static/sounds/wait.wav
```
*ya existe el archivo 'wait.wav'*
