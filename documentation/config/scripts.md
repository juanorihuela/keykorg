# Configuración: Scripts — KeyKorg

Cubre la creación y referencia de scripts en `src/static/scripts/`. Soporta `.sh` y `.py`. No requiere tocar código Python del sistema.

---

## Agregar un script nuevo

Cada comando que requiera un script de shell tiene su propio archivo `.sh` en `src/static/scripts/`.

**Paso 1** — Crear `src/static/scripts/mi_script.sh` basándose en `scripts/examples/script.example.sh`:

```bash
#!/bin/bash
sleep 0.3
xdotool type "mi-comando"
sleep 0.3
xdotool key Return
```

**Paso 2** — Darle permisos de ejecución:

```bash
chmod +x src/static/scripts/mi_script.sh
```

**Paso 3** — Referenciarlo en el YAML con path relativo:

```yaml
pads:
  44:
    name: "Mi Script"
    type: sequence
    steps:
      - action: shell
        command: "src/static/scripts/mi_script.sh"
```

El path se resuelve automáticamente. No hardcodear el path absoluto en el YAML.

Los scripts personales están en `.gitignore` (`src/static/scripts/*`). El directorio `scripts/examples/` sí se versiona.

---

## Agregar un script Python nuevo

Útil cuando el script necesita lógica más compleja: manipular fechas, llamar APIs, formatear output, etc.

**Paso 1** — Crear `src/static/scripts/mi_script.py` basándose en `scripts/examples/hello_keykorg.py`:

```python
import subprocess
from datetime import datetime

NOW = datetime.now().strftime("%H:%M")
message = f"Reporte generado — {NOW}"
print(message)

subprocess.run(
    ["notify-send", "Mi Script", message, "--icon=dialog-information"],
    check=False,
)
```

**Paso 2** — Referenciarlo en el YAML con `python` como ejecutable:

```yaml
pads:
  45:
    name: "Mi Script Python"
    type: sequence
    steps:
      - action: shell
        command: "python src/static/scripts/mi_script.py"
        wait: true
```

No se necesita `chmod`. El path relativo se resuelve automáticamente igual que con los `.sh`.
