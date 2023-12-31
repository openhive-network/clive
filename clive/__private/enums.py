from __future__ import annotations

from enum import Enum


class AppMode(str, Enum):
    """Application mode."""

    value: str

    INACTIVE = "inactive"
    ACTIVE = "active"
