from dataclasses import dataclass
from datetime import datetime


@dataclass
class PadEvent:
    pad_id: int
    velocity: int
    timestamp: datetime
