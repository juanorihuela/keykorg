import shlex
import subprocess
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SequenceService:
    def execute(self, steps: list[dict[str, Any]], pad_name: str) -> bool:
        try:
            for step in steps:
                self._run_step(step)
            logger.info(f"SEQ_OK | name={pad_name!r}")
            return True
        except Exception as ex:
            logger.error(f"SEQ_FAIL | name={pad_name!r} | error={type(ex).__name__}: {ex}")
            return False

    def _run_step(self, step: dict[str, Any]) -> None:
        action = step.get("action")

        if action == "close_all":
            subprocess.Popen(["wmctrl", "-k", "on"])

        elif action == "open":
            app = step.get("app", "")
            subprocess.Popen(shlex.split(app))

        elif action == "notify":
            message = step.get("message", "")
            subprocess.Popen(["notify-send", message])

        elif action == "delay":
            time.sleep(float(step.get("seconds", 1)))

        elif action == "shell":
            command = step.get("command", "")
            subprocess.Popen(shlex.split(command))

        else:
            logger.warning(f"SEQ_UNKNOWN_ACTION | action={action!r}")
