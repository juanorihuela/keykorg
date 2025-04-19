"""
Dict de comandos disponibles para el dispositivo
Key:
    int, con la nota del pad que se quiere mapear
Value:
    list, con el comando para ejecutar en segmentos str
"""
MIDI_TO_COMMAND = {
    36: ["gnome-terminal", "--", "bash", "-c", "cd ~/ && exec bash"],  # terminal

    37: ["google-chrome"],  # chrome
    38: ["spotify"],  # spotify
    39: ["/opt/Postman/Postman"],  #postman
    40: ["/var/lib/flatpak/app/io.dbeaver.DBeaverCommunity/x86_64/stable/cc737e000cd13ebe4e93b33a5f6a0d877296c6e2ba12b11c9f094909213f8f7c/files/bin/dbeaver"],  #dbeaver

    44: ["src/static/scripts/code_here.sh"],  # ejecuta script
    46: ["src/static/scripts/react_localhost.sh"],  # ejecuta script

    48: ["xdotool", "key", "ctrl+alt+l"],  # bloquear pantalla
    49: ["notify-send", "Pad", "Hey!"],  # enviar notificación

    50: ["espeak", "-v", "es", "arriba la maquina perros"],  # reproducir mensaje
    51: ["espeak", "-v", "es", "payaso"]
}
