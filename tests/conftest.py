from datetime import datetime

import pytest

from dtos.pad_event import PadEvent


def make_pad_event(pad_id: int = 1, velocity: int = 100) -> PadEvent:
    return PadEvent(pad_id=pad_id, velocity=velocity, timestamp=datetime.now())
