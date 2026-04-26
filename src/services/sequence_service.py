import shlex
import subprocess
import time
import logging
from typing import Any

from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class SequenceService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self, steps: list[dict[str, Any]], pad_name: str) -> bool:
        try:
            for step in steps:
                self._run_step(step)
            logger.info(f"SEQ_OK | name={pad_name!r}")
            return True
        except Exception as ex:
            logger.error(f"SEQ_FAIL | name={pad_name!r} | error={type(ex).__name__}: {ex}")
            self.notification_service.notify_alert(pad_name, "Error en secuencia")
            return False

    def _run_step(self, step: dict[str, Any]) -> None:
        action = step.get("action")

        if action == "close_all":
            result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
            window_ids = [line.split()[0] for line in result.stdout.splitlines() if line.split()]
            for wid in window_ids:
                subprocess.run(["wmctrl", "-ic", wid])
            time.sleep(1.0)

        elif action == "open":
            app = step.get("app", "")
            subprocess.Popen(shlex.split(app))

        elif action == "notify":
            if "sound" in step:
                self.notification_service.play_sound(step["sound"])
            elif "message" in step:
                subprocess.Popen(["notify-send", step["message"]])

        elif action == "delay":
            time.sleep(float(step.get("seconds", 1)))

        elif action == "shell":
            command = step.get("command", "")
            subprocess.Popen(shlex.split(command))

        else:
            logger.warning(f"SEQ_UNKNOWN_ACTION | action={action!r}")
