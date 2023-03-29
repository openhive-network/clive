from __future__ import annotations

from dataclasses import dataclass

from clive.__private.enums import AppMode


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    mode: AppMode = AppMode.INACTIVE

    def is_active(self) -> bool:
        return self.mode == AppMode.ACTIVE

    def activate(self) -> None:
        self.mode = AppMode.ACTIVE

    def deactivate(self) -> None:
        self.mode = AppMode.INACTIVE
