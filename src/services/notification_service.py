import subprocess
import logging
from pathlib import Path

from helpers.os_helpers import get_sound_player

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, sounds_dir: Path, volume: float = 0.7):
        self.sounds_dir = sounds_dir
        self.volume = volume

    def notify_success(self, title: str, message: str = "") -> None:
        self._notify(title, message)
        self._play_sound("success.wav")

    def notify_sequence(self) -> None:
        self._play_sound("sequence.wav")

    def play_sound(self, filename: str) -> None:
        self._play_sound(filename)

    def notify_done(
        self,
        title: str,
        message: str = "",
        *,
        skip_notify: bool = False,
        skip_sound: bool = False,
    ) -> None:
        if not skip_notify:
            self._notify(title, message)
        if not skip_sound:
            self._play_sound("done.wav")

    def notify_warning(self, title: str, message: str = "") -> None:
        self._notify(title, message)
        self._play_sound("warning.wav")

    def notify_alert(self, title: str, message: str = "") -> None:
        self._notify(title, message)
        self._play_sound("alert.wav")

    def notify_bye(self, title: str, message: str = "") -> None:
        self._notify(title, message)
        self._play_sound("bye.wav")

    def _notify(self, title: str, message: str) -> None:
        try:
            subprocess.Popen(["notify-send", title, message])
        except Exception as ex:
            logger.error(f"NOTIFY_FAIL | error={ex}")

    def _play_sound(self, filename: str) -> None:
        sound_path = self.sounds_dir / filename
        if not sound_path.exists():
            logger.warning(f"SOUND_NOT_FOUND | path={sound_path}")
            return
        player = get_sound_player(self.volume)
        if not player:
            logger.warning("SOUND_NO_PLAYER | no se encontró reproductor de audio")
            return
        try:
            subprocess.Popen([*player, str(sound_path)])
        except Exception as ex:
            logger.error(f"SOUND_FAIL | path={sound_path} | error={ex}")
