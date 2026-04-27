# KeyKorg — Documentación

Archivo raíz. Cada sección enlaza a la documentación específica.

---

## Punto de entrada

| Documento | Qué cubre |
|---|---|
| [arquitectura.md](arquitectura.md) | Descripción general, estructura de directorios, capas y flujo de datos |
| [reglas_de_codigo.md](reglas_de_codigo.md) | Convenciones de código, estructura, OOP, manejo de errores |

---

## Piezas del sistema

| Documento | Qué cubre |
|---|---|
| [piezas_clave/config.md](piezas_clave/config.md) | `constants.py`, `settings.py`, `log_config.py` |
| [piezas_clave/core_y_dtos.md](piezas_clave/core_y_dtos.md) | `midi_listener.py`, `pad_event.py` |
| [piezas_clave/services.md](piezas_clave/services.md) | `command_service.py`, `sequence_service.py`, `notification_service.py` |
| [piezas_clave/handlers_y_helpers.md](piezas_clave/handlers_y_helpers.md) | `pad_handler.py`, `os_helpers.py`, referencia a `config/commands/` |

---

## Configuración

| Documento | Qué cubre |
|---|---|
| [config/logging.md](config/logging.md) | Sistema de logs, formato de línea, convenciones, catálogo de eventos |
| [config/yaml_comandos.md](config/yaml_comandos.md) | Estructura YAML de pads, reglas, agregar pad o escenario nuevo |
| [config/scripts.md](config/scripts.md) | Agregar scripts de shell en `src/static/scripts/` |

---

## Guía para devs e IA

| Documento | Qué cubre |
|---|---|
| [guia_devs/onboarding.md](guia_devs/onboarding.md) | Orden recomendado para leer y entender el proyecto |
| [guia_devs/integraciones.md](guia_devs/integraciones.md) | Cómo integrar cambios: acciones, SOs, notificaciones, servicios |
| [guia_devs/patrones_y_checklist.md](guia_devs/patrones_y_checklist.md) | Patrones obligatorios, qué no hacer, checklist de verificación |
