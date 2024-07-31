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
    _is_unlocked: bool = False

    @property
    def is_unlocked(self) -> bool:
        return self._is_unlocked

    def unlock(self) -> None:
        self._is_unlocked = True
        logger.info("Mode switched to UNLOCKED.")

    def lock(self) -> None:
        self._is_unlocked = False
        logger.info("Mode switched to LOCKED.")

    def __hash__(self) -> int:
        return id(self.world)
