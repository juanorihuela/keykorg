import shlex
from pathlib import Path

import yaml
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
            raise FileNotFoundError(
                f"Archivo de configuración '{env_file}' no encontrado"
            )

        values = dotenv_values(env_file)
        self.midi_device: str = values["MIDI_DEVICE"]
        self.sounds_dir: Path = PROJECT_ROOT / values["SOUNDS_DIR"]
        self.commands_file: Path = PROJECT_ROOT / values["COMMANDS_FILE"]
        self.log_level: str = values.get("LOG_LEVEL", "INFO")

    def load_pad_map(self) -> dict:
        try:
            with open(self.commands_file) as f:
                root = yaml.safe_load(f)

            imports = root.get("imports", [])
            if imports:
                pad_map = {}
                commands_dir = self.commands_file.parent
                for rel_path in imports:
                    file_path = commands_dir / rel_path
                    with open(file_path) as f:
                        data = yaml.safe_load(f)
                    pad_map.update(data.get("pads", {}))
            else:
                pad_map = root.get("pads", {})

            return self._resolve_paths(pad_map)
        except FileNotFoundError as ex:
            msg = f"Archivo de comandos no encontrado: {ex.filename}"
            raise FileNotFoundError(msg) from ex
        except yaml.YAMLError as ex:
            raise ValueError(f"YAML malformado: {ex}") from ex

    def _resolve_paths(self, pad_map: dict) -> dict:
        for pad_config in pad_map.values():
            pad_type = pad_config.get("type")
            if pad_type == "simple":
                pad_config["command"] = self._resolve_cmd(pad_config.get("command", ""))
            elif pad_type == "sequence":
                for step in pad_config.get("steps", []):
                    action = step.get("action")
                    if action == "open":
                        step["app"] = self._resolve_cmd(step.get("app", ""))
                    elif action == "shell":
                        step["command"] = self._resolve_cmd(step.get("command", ""))
        return pad_map

    def _resolve_cmd(self, command: str) -> str:
        tokens = shlex.split(command)
        if not tokens:
            return command
        candidate = PROJECT_ROOT / tokens[0]
        if candidate.is_file():
            tokens[0] = str(candidate)
            return shlex.join(tokens)
        return command

    def _validate_so(self, so: str) -> None:
        if so not in SO_CATALOG:
            available = list(SO_CATALOG.keys())
            raise ValueError(
                f"SO '{so}' no está en el catálogo. Disponibles: {available}"
            )

        host = get_host_so()
        if host is not None and host != so:
            raise ValueError(
                f"SO anfitrión es '{host}', no se puede ejecutar en modo '{so}'"
            )
