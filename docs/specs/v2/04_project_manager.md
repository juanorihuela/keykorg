# KeyKorg — Spec: ProjectManager

## Contexto

El script `end_of_day.py` usa una ruta estática `PROJECTS_DIR` y trae todos los proyectos
del directorio. Se necesita una clase `ProjectManager` que centralice la configuración
de proyectos y la comparta entre el reporte de fin de jornada y las secuencias de modos.

---

## DTO — `src/dtos/project.py`

```python
@dataclass
class Project:
    name: str
    stack: str    # "front" | "back"
    path: Path    # resuelto a absoluto en load()
    dev_command: str
```

---

## Archivo de configuración — `src/config/projects.yaml`

Agregar al `.gitignore`. Versionar `src/config/projects.example.yaml` como template.

```yaml
# projects.example.yaml
projects:
  - name: "mi-proyecto-back"
    stack: back
    path: "~/projects/back/mi-proyecto"
    dev_command: "python manage.py runserver"

  - name: "mi-proyecto-front"
    stack: front
    path: "~/projects/front/mi-proyecto"
    dev_command: "yarn dev"
```

---

## Clase — `src/services/project_manager.py`

**Atributos:**

```python
self.projects: list[Project]
self.front_projects: list[Project]
self.back_projects: list[Project]
self.active_project: Project | None
self._state_file: Path  # ~/.keykorg_state.json
```

**Métodos:**

```python
def load(self, projects_file: Path) -> None
    # Lee projects.yaml
    # Resuelve paths con Path.expanduser()
    # Valida que cada path exista — logger.warning si no existe
    # Popula self.projects, self.front_projects, self.back_projects
    # Maneja FileNotFoundError y yaml.YAMLError con mensajes descriptivos

def select_project(self, scope: str) -> Project | None
    # CLI interactivo en terminal
    # scope: "front" | "back" | "full"
    # Muestra lista numerada de proyectos según scope
    # Recibe índice del usuario
    # Guarda el proyecto seleccionado en self.active_project
    # Persiste en ~/.keykorg_state.json via _save_state()
    # Retorna el Project seleccionado o None si el usuario cancela

def get_day_report(self, scope: str) -> str
    # Genera reporte de actividad git del día
    # scope: "front" | "back" | "full"
    # Itera sobre proyectos del scope
    # Por cada proyecto: commits del día, archivos modificados, unpushed
    # Retorna el reporte como string en formato markdown

def save_report(self, content: str) -> Path
    # Guarda en ~/reports/eod_YYYY-MM-DD.md
    # Crea el directorio si no existe
    # Retorna el Path del archivo generado

def _save_state(self) -> None
    # Serializa self.active_project a ~/.keykorg_state.json

def _load_state(self) -> Project | None
    # Lee ~/.keykorg_state.json
    # Retorna el Project activo o None si no existe el archivo
```

---

## CLI — `src/static/scripts/select_project.py`

```bash
python src/static/scripts/select_project.py back
python src/static/scripts/select_project.py front
python src/static/scripts/select_project.py full
```

Flujo en terminal:

```
== Proyectos back ==
1. armando          ~/projects/back/armando
2. asesoriaselecta  ~/projects/back/asesoriaselecta

Selecciona un proyecto (q para cancelar): _
```

Al seleccionar, guarda el estado en `~/.keykorg_state.json` y termina el proceso.
El cierre del proceso es la señal para que la secuencia continúe (via `wait: true`).

---

## CLI — `src/static/scripts/end_of_day.py`

```bash
python src/static/scripts/end_of_day.py full
python src/static/scripts/end_of_day.py back
python src/static/scripts/end_of_day.py front
```

Flujo:

1. Recibe `scope` como argumento obligatorio — error descriptivo si falta
2. Instancia `ProjectManager`, llama `load(projects_file)`
3. Llama `get_day_report(scope)`
4. Llama `save_report(content)`
5. Abre el archivo generado con `subprocess.Popen(["gnome-terminal", "--", "nano", str(report_path)])`

---

## Script — `src/static/scripts/run_dev.sh`

Lee `~/.keykorg_state.json` y ejecuta el `dev_command` del proyecto activo
en el directorio correcto:

```bash
#!/bin/bash
# run_dev.sh — ejecuta el dev_command del proyecto activo

STATE="$HOME/.keykorg_state.json"

if [ ! -f "$STATE" ]; then
    notify-send "KeyKorg" "No hay proyecto activo. Selecciona uno primero."
    exit 1
fi

PROJECT_PATH=$(python3 -c "import json; d=json.load(open('$STATE')); print(d['active_project']['path'])")
DEV_CMD=$(python3 -c "import json; d=json.load(open('$STATE')); print(d['active_project']['dev_command'])")

gnome-terminal -- bash -c "cd '$PROJECT_PATH' && $DEV_CMD; exec bash"
```

---

## Integración con secuencias

Con `wait: true` (ver spec 03) el delay fijo de 8s desaparece — la secuencia espera a que
el usuario seleccione y el CLI termine antes de continuar:

```yaml
49:
  name: "Modo Back"
  type: sequence
  steps:
    - action: shell
      command: "gnome-terminal -- bash -c 'python src/static/scripts/select_project.py back; exec bash'"
      wait: true
      wait_threshold: 2
    - action: open
      app: "flatpak run io.dbeaver.DBeaverCommunity"
    - action: delay
      seconds: 0.5
    - action: shell
      command: "/opt/Postman/Postman"
    - action: shell
      command: "src/static/scripts/open_chrome.sh"
    - action: delay
      seconds: 0.5
    - action: shell
      command: "src/static/scripts/run_dev.sh"
    - action: open
      app: "spotify"

50:
  name: "Modo Front"
  type: sequence
  steps:
    - action: shell
      command: "gnome-terminal -- bash -c 'python src/static/scripts/select_project.py front; exec bash'"
      wait: true
      wait_threshold: 2
    - action: shell
      command: "src/static/scripts/open_chrome.sh http://localhost:3000"
    - action: delay
      seconds: 0.5
    - action: shell
      command: "src/static/scripts/run_dev.sh"
    - action: open
      app: "spotify"

51:
  name: "Fin de jornada"
  type: sequence
  steps:
    - action: shell
      command: "src/static/scripts/cleanup.sh"
    - action: delay
      seconds: 1.0
    - action: shell
      command: "python src/static/scripts/end_of_day.py full"
      wait: true
      wait_threshold: 2
    - action: delay
      seconds: 1.0
    - action: shell
      command: "xdotool key ctrl+alt+l"
```

---

## Archivos nuevos a crear

```
src/dtos/project.py
src/services/project_manager.py
src/static/scripts/select_project.py
src/static/scripts/end_of_day.py        # reemplaza el actual
src/static/scripts/run_dev.sh
src/config/projects.example.yaml
```

## Archivos a agregar en `.gitignore`

```
src/config/projects.yaml
.keykorg_state.json
reports/
```

## Archivos a versionar

```
src/config/projects.example.yaml
src/static/scripts/run_dev.sh
src/static/scripts/select_project.py
src/static/scripts/end_of_day.py
```
