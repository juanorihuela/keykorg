#!/bin/bash
#
# ==============================================================================
# EJEMPLO: Script de shell para KeyKorg
# ==============================================================================
#
# ¿Para qué sirven los scripts?
#   Cuando una acción de pad necesita escribir texto en una terminal, encadenar
#   comandos o interactuar con el foco actual del teclado, un script .sh es la
#   herramienta correcta. Los comandos simples (type: simple) solo abren un
#   proceso; los scripts permiten hacer todo lo demás.
#
# ──────────────────────────────────────────────────────────────────────────────
# CÓMO CREAR UN SCRIPT NUEVO
#
#   1. Crear el archivo en src/static/scripts/:
#        cp src/static/scripts/examples/script.example.sh src/static/scripts/mi_script.sh
#
#   2. Darle permisos de ejecución:
#        chmod +x src/static/scripts/mi_script.sh
#
#   3. Referenciarlo en el YAML del escenario correspondiente:
#
#        # Como type: simple (el script es la única acción del pad):
#        42:
#          name: "Mi Acción"
#          type: simple
#          command: "src/static/scripts/mi_script.sh"
#
#        # Como paso dentro de una sequence (acción: shell):
#        43:
#          name: "Mi Secuencia"
#          type: sequence
#          steps:
#            - action: open
#              app: "gnome-terminal"
#            - action: delay
#              seconds: 0.5
#            - action: shell
#              command: "src/static/scripts/mi_script.sh"
#
#   El path relativo se resuelve automáticamente contra PROJECT_ROOT.
#   No hace falta hardcodear el path absoluto en el YAML.
#
# ──────────────────────────────────────────────────────────────────────────────
# NOTAS SOBRE xdotool
#   xdotool type "texto"   → escribe el texto en la ventana con foco actual
#   xdotool key Return     → presiona Enter
#   xdotool key ctrl+c     → simula Ctrl+C
#
#   Es importante agregar un sleep antes de xdotool type para asegurar que
#   la ventana destino ya tiene el foco antes de escribir.
# ==============================================================================

# Espera a que la ventana destino tenga foco
sleep 0.3

# Escribe el comando en la terminal activa
xdotool type "mi-comando"

# Pequeña pausa antes de confirmar (opcional, pero recomendada)
sleep 0.3

# Presiona Enter para ejecutar
xdotool key Return
