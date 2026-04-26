import shlex
import subprocess
import logging

from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class CommandService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self, command: str, pad_name: str) -> bool:
        try:
            args = shlex.split(command)
            subprocess.Popen(args)
            logger.info(f"CMD_OK | name={pad_name!r} | command={command!r}")
            return True
        except FileNotFoundError as ex:
            logger.warning(f"CMD_NOT_FOUND | name={pad_name!r} | command={command!r} | error={ex}")
            self.notification_service.notify_warning(pad_name, "Comando no encontrado")
            return False
        except Exception as ex:
            logger.error(f"CMD_FAIL | name={pad_name!r} | command={command!r} | error={type(ex).__name__}: {ex}")
            self.notification_service.notify_alert(pad_name, "Error al ejecutar comando")
            return False
