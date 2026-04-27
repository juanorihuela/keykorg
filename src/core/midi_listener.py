import logging
import time
from collections.abc import Callable
from datetime import datetime

import mido

from config.constants import CONNECTION_DELAY, CONNECTION_RETRIES
from dtos.pad_event import PadEvent

logger = logging.getLogger(__name__)


class MidiListener:
    def __init__(self, device_name: str, on_pad_press: Callable[[PadEvent], None]):
        self.device_name = device_name
        self.on_pad_press = on_pad_press

    @staticmethod
    def wait_for_connection(
        device_name: str,
        retries: int = CONNECTION_RETRIES,
        delay: int = CONNECTION_DELAY,
    ) -> bool:
        for _ in range(retries):
            logger.info("conectando...")
            if any(device_name in d for d in mido.get_input_names()):
                return True
            time.sleep(delay)
        return False

    def _resolve_device(self) -> str:
        matches = [d for d in mido.get_input_names() if self.device_name in d]
        if not matches:
            raise RuntimeError(f"Dispositivo MIDI '{self.device_name}' no encontrado")
        return matches[0]

    def listen(self) -> None:
        device_port = self._resolve_device()
        active_notes: set = set()

        with mido.open_input(device_port) as device:
            logger.info("escuchando midi...")
            for msg in device:
                if msg.type == "note_on" and msg.velocity > 0:
                    if msg.note not in active_notes:
                        active_notes.add(msg.note)
                        event = PadEvent(
                            pad_id=msg.note,
                            velocity=msg.velocity,
                            timestamp=datetime.now(),
                        )
                        self.on_pad_press(event)
                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    active_notes.discard(msg.note)
