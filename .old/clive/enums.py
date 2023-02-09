from __future__ import annotations

from enum import Enum, auto


class AppMode(Enum):
    """Application mode"""

    INACTIVE = auto()
    ACTIVE = auto()
    ANY = auto()
