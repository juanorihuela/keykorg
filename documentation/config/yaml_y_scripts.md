# Configuración: YAML, Scripts y Sonidos — KeyKorg

Cubre la configuración basada en archivos: comandos YAML de pads, scripts de shell y sonidos estáticos. No requiere tocar código Python.

---

## Estructura de `config/commands/`

Organizado por SO. Cada SO tiene:
- Un archivo raíz `commands.{so}.yaml` que solo lista imports
- Un subdirectorio `{so}/` con un archivo YAML por escenario o categoría

**Archivo raíz** (`commands.debian.yaml`):
```yaml
imports:
  - debian/scene_1.yaml
```

**Archivo de escenario** (`debian/scene_1.yaml`):
```yaml
pads:
  {pad_id: int}:
    name: str          # nombre descriptivo, aparece en logs y notificaciones
    type: simple | sequence
    command: str       # solo si type=simple — parseado con shlex, paths resueltos automáticamente
    steps: list        # solo si type=sequence
    skip_notify: bool  # opcional, default false — omite la notificación visual al completar
    skip_sound: bool   # opcional, default false — omite el sonido al completar
```

`Settings.load_pad_map()` carga el raíz, itera los imports y mergea todos los `pads` en un dict único. Si no hay `imports:`, carga `pads:` directamente (compatibilidad con formato anterior).

Los templates de referencia viven en `{so}/example/` y se versionan. Los archivos reales (`commands.{so}.yaml` y `{so}/*.yaml`) están en `.gitignore`.

Los `pad_id` son las notas MIDI del dispositivo. Para el nanoPAD2 van del 36 al 51.

---

## Reglas de YAML

- El archivo raíz `commands.{so}.yaml` solo contiene `imports:` — no define pads directamente
- Los pads se definen en archivos de escenario dentro de `{so}/`, uno por categoría
- El campo `name` es obligatorio — aparece en logs y notificaciones
- El `pad_id` es la nota MIDI del dispositivo (entero)
- Los comandos `simple` usan strings completos parseados con `shlex.split`
- Los paths relativos en comandos se resuelven automáticamente contra `PROJECT_ROOT` en `Settings.load_pad_map()`
- Las secuencias usan solo las acciones definidas: `open`, `close_all`, `notify`, `delay`, `shell`

---

## Agregar un pad nuevo

Editar el archivo de escenario correspondiente en `src/config/commands/debian/`. No tocar código Python.

```yaml
pads:
  42:
    name: "Mi App"
    type: simple
    command: "nombre-del-binario"
```

Para secuencias:

```yaml
pads:
  43:
    name: "Mi Secuencia"
    type: sequence
    steps:
      - action: open
        app: "gnome-terminal"
      - action: delay
        seconds: 1
      - action: shell
        command: "mi-comando"
```

Los paths relativos (ej: `src/static/scripts/mi_script.sh`) se resuelven automáticamente a absolutos en `Settings.load_pad_map()`.

---

## Agregar un escenario nuevo

**Paso 1** — Crear el archivo de escenario en `src/config/commands/debian/mi_escenario.yaml`:

```yaml
pads:
  50:
    name: "Mi App"
    type: simple
    command: "mi-app"
```

**Paso 2** — Registrarlo en el archivo raíz `commands.debian.yaml`:

```yaml
imports:
  - debian/apps.yaml
  - debian/dev.yaml
  - debian/mi_escenario.yaml   # nuevo
```

El archivo de escenario es personal y queda ignorado por `.gitignore`. Si querés que otros lo usen como referencia, creá el equivalente en `debian/example/mi_escenario.example.yaml` — ese sí se versiona.

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

