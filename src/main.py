import mido
import logging
import time
import subprocess

from exceptions.connection_failed import ConnectionFailedException

from static.commands import MIDI_TO_COMMAND


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KeyKorg:
    device_name = "nanoPAD2:nanoPAD2 nanoPAD2 _ CTRL"

    def validate_connection(self) -> bool:
        """
        Valida que el MIDI está dentro de la lista de
        dispositivos conectados
        """
        devices = [device for device in mido.get_input_names() if self.device_name in device]

        return any(devices)

    def wait_for_connection(self, retries = 3, delay = 2):
        """
        Realiza n intentos de conexión al dispositivo agregando
        un tiempo de espera entre cada intento
        Args:
            retries: int, con la cantidad máxima de intentos
            delay: int, con la cantidad de tiempo de espera
        """
        for _ in range(retries):
            logger.info("conectando...")
            if self.validate_connection():
                return True
            time.sleep(delay)
        return False

    def listener(self):
        """
        Se mantiene escuchando los inputs del dispositivo conectado
        """
        active_notes = set()
        with mido.open_input(self.device_name) as device:
            logger.info("escuchando midi...")
            for msg in device:
                if msg.type == "note_on" and msg.velocity > 0:
                    if not msg.note in active_notes:
                        active_notes.add(msg.note)
                        command = MIDI_TO_COMMAND.get(msg.note)
                        if command:
                            logger.info(f"ejecutando -> {command}")
                            subprocess.Popen(command)
                            logger.info("hecho")
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    active_notes.discard(msg.note)

    def execute(self):
        """
        Ejecuta el script y se mantiene escuchando los mensajes del MIDI
        """
        try:
            logger.info("Iniciando KeyKorg")
            if not self.wait_for_connection():
                raise ConnectionFailedException("No se encuentra el dispositivo")
            self.listener()

        except KeyboardInterrupt as key_ex:
            logger.info(key_ex)

        except ConnectionFailedException as con_ex:
            logger.error(f"connection -> {con_ex}")

        except Exception as ex:
            logger.error(f"general -> {ex}")

KeyKorg().execute()
