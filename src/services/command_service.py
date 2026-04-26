import shlex
import subprocess
import logging

logger = logging.getLogger(__name__)


class CommandService:
    def execute(self, command: str, pad_name: str) -> bool:
        try:
            args = shlex.split(command)
            subprocess.Popen(args)
            logger.info(f"CMD_OK | name={pad_name!r} | command={command!r}")
            return True
        except FileNotFoundError as ex:
            logger.error(f"CMD_FAIL | name={pad_name!r} | command={command!r} | error=FileNotFoundError: {ex}")
            return False
        except Exception as ex:
            logger.error(f"CMD_FAIL | name={pad_name!r} | command={command!r} | error={type(ex).__name__}: {ex}")
            return False
