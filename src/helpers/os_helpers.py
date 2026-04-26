import platform
import shutil

_HOST_SO_MAP = {
    "linux": "mint",
    "darwin": "macos",
}


def get_host_so() -> str | None:
    system = platform.system().lower()
    return _HOST_SO_MAP.get(system)


def get_sound_player() -> list[str]:
    for player in ("aplay", "paplay", "afplay"):
        if shutil.which(player):
            return [player]
    return []
