import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from config.constants import LOG_BACKUP_COUNT

_LOG_DIR = Path(__file__).parent.parent.parent / "logs"
_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)-5s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class LogConfig:
    @classmethod
    def setup(cls, log_level: str) -> None:
        _LOG_DIR.mkdir(exist_ok=True)

        file_handler = TimedRotatingFileHandler(
            _LOG_DIR / "keykorg.log",
            when="midnight",
            backupCount=LOG_BACKUP_COUNT,
        )
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.setFormatter(_FORMATTER)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(_FORMATTER)

        root = logging.getLogger()
        root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        root.addHandler(file_handler)
        root.addHandler(console_handler)
