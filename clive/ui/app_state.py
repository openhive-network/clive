from __future__ import annotations

from dataclasses import dataclass

from clive.enums import AppMode


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    mode: AppMode = AppMode.INACTIVE
    permanent_active: bool = False

    def is_active(self) -> bool:
        return self.mode == AppMode.ACTIVE
