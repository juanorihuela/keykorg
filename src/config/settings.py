import yaml
from pathlib import Path
from dotenv import dotenv_values

from config.constants import SO_CATALOG
from helpers.os_helpers import get_host_so

PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings:
    def __init__(self, so: str):
        self._validate_so(so)
        self.so = so
        self.is_pending = SO_CATALOG[so] == "pending"

        env_file = PROJECT_ROOT / f".env.{so}"
        if not env_file.exists():
            raise FileNotFoundError(f"Archivo de configuración '{env_file}' no encontrado")

        values = dotenv_values(env_file)
        self.midi_device: str = values["MIDI_DEVICE"]
        self.sounds_dir: Path = PROJECT_ROOT / values["SOUNDS_DIR"]
        self.commands_file: Path = PROJECT_ROOT / values["COMMANDS_FILE"]
        self.log_level: str = values.get("LOG_LEVEL", "INFO")

    def load_pad_map(self) -> dict:
        with open(self.commands_file, "r") as f:
            data = yaml.safe_load(f)
        return data.get("pads", {})

    def _validate_so(self, so: str) -> None:
        if so not in SO_CATALOG:
            available = list(SO_CATALOG.keys())
            raise ValueError(f"SO '{so}' no está en el catálogo. Disponibles: {available}")

        host = get_host_so()
        if host is not None and host != so:
            raise ValueError(f"SO anfitrión es '{host}', no se puede ejecutar en modo '{so}'")
