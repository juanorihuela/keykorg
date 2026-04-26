import platform
import shutil

_HOST_SO_MAP = {
    "linux": "debian",
    "darwin": "macos",
}


def get_host_so() -> str | None:
    system = platform.system().lower()
    return _HOST_SO_MAP.get(system)


def get_sound_player(volume: float = 1.0) -> list[str]:
    # paplay primero: soporta control de volumen nativo (0–65536)
    if shutil.which("paplay"):
        int_vol = int(volume * 65536)
        return ["paplay", f"--volume={int_vol}"]
    if shutil.which("afplay"):
        return ["afplay", "-v", str(round(volume, 2))]
    if shutil.which("aplay"):
        return ["aplay"]  # sin control de volumen por comando
    return []
