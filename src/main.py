import argparse
import logging
import sys

from config.constants import SO_CATALOG
from config.log_config import LogConfig
from config.settings import Settings
from core.midi_listener import MidiListener
from handlers.pad_handler import PadHandler
from services.command_service import CommandService
from services.sequence_service import SequenceService
from services.notification_service import NotificationService
from exceptions.connection_failed import ConnectionFailedException

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="KeyKorg MIDI controller")
    parser.add_argument("--so", required=True, choices=list(SO_CATALOG.keys()))
    args = parser.parse_args()

    try:
        settings = Settings(args.so)
    except (ValueError, FileNotFoundError) as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)

    LogConfig.setup(settings.log_level)
    logger.info("Iniciando KeyKorg")

    notifier = NotificationService(settings.sounds_dir)

    if settings.is_pending:
        msg = f"SO '{settings.so}' aún no está soportado"
        logger.error(msg)
        notifier.notify_alert("KeyKorg", msg)
        sys.exit(1)

    try:
        if not MidiListener.wait_for_connection(settings.midi_device):
            raise ConnectionFailedException("No se encuentra el dispositivo")

        notifier.notify_success("KeyKorg conectado ✓")

        handler = PadHandler(
            pad_map=settings.load_pad_map(),
            command_service=CommandService(notifier),
            sequence_service=SequenceService(notifier),
            notification_service=notifier,
        )

        MidiListener(settings.midi_device, handler.handle).listen()

    except KeyboardInterrupt:
        logger.info("KeyKorg detenido por el usuario")
        notifier.notify_bye("KeyKorg", "Saliendo")

    except ConnectionFailedException as ex:
        logger.error(f"CONNECTION_FAIL | error={ex}")
        notifier.notify_alert("No se pudo conectar a KeyKorg")

    except Exception as ex:
        logger.error(f"GENERAL_ERROR | error={type(ex).__name__}: {ex}")
        notifier.notify_alert("KeyKorg", f"Error inesperado: {type(ex).__name__}")


if __name__ == "__main__":
    main()
