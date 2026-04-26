#!/bin/bash

# Este script es un ejemplo de cómo crear scripts para KeyKorg.
# Los scripts se invocan desde el YAML de comandos usando type: sequence + action: shell.
#
# Ejemplo de uso en commands.debian.yaml:
#
#   pads:
#     42:
#       name: "Mi Script"
#       type: sequence
#       steps:
#         - action: shell
#           command: "src/static/scripts/mi_script.sh"
#
# El path relativo se resuelve automáticamente a absoluto en Settings.load_pad_map().
# No hace falta hardcodear el path completo en el YAML.

# Espera opcional para asegurar que el foco esté en la ventana correcta
sleep 0.3

# Escribir texto en el foco actual (requiere xdotool)
xdotool type "mi-comando"

# Esperar antes de ejecutar
sleep 0.3

# Presionar Enter
xdotool key Return
