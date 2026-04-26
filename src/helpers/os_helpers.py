import shutil


def get_sound_player() -> list[str]:
    for player in ("aplay", "paplay", "afplay"):
        if shutil.which(player):
            return [player]
    return []
