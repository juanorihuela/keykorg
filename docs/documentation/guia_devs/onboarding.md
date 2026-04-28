# Guía para Devs e IA — Onboarding

Orden recomendado para leer y entender el sistema antes de hacer cambios.

---

## Orden de lectura

1. [../arquitectura.md](../arquitectura.md) — visión general y flujo de datos
2. [../piezas_clave/config.md](../piezas_clave/config.md) — constants, settings, log_config
3. [../piezas_clave/core_y_dtos.md](../piezas_clave/core_y_dtos.md) — midi_listener, pad_event
4. [../piezas_clave/handlers_y_helpers.md](../piezas_clave/handlers_y_helpers.md) — pad_handler, os_helpers
5. [../piezas_clave/services.md](../piezas_clave/services.md) — command_service, sequence_service, notification_service
6. [../reglas_de_codigo.md](../reglas_de_codigo.md) — convenciones a respetar
7. [../config/yaml_comandos.md](../config/yaml_comandos.md) — configuración de pads
8. [../config/scripts.md](../config/scripts.md) — scripts de shell
9. [../config/logging.md](../config/logging.md) — sistema de logs, formato y convenciones
10. [../herramientas/tooling.md](../herramientas/tooling.md) — Makefile, Ruff, pyproject.toml
11. [../herramientas/tests.md](../herramientas/tests.md) — estructura de tests, coverage, convenciones
12. `src/config/constants.py` — constantes del sistema
13. `src/config/settings.py` — cómo se carga la configuración
14. `src/main.py` — punto de entrada, flujo de arranque
15. `src/config/commands/commands.debian.example.yaml` — template raíz (imports)
16. `src/config/commands/debian/example/apps.example.yaml` — template de escenario
