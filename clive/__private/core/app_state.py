from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.world import World


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World
    _is_active: bool = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def activate(self) -> None:
        self._is_active = True
        logger.info("Mode switched to ACTIVE.")

    def deactivate(self) -> None:
        self._is_active = False
        logger.info("Mode switched to INACTIVE.")

    def __hash__(self) -> int:
        return id(self.world)
