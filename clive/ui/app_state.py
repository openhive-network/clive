from __future__ import annotations

from dataclasses import dataclass

from clive.enums import AppMode


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    mode: AppMode = AppMode.INACTIVE
