from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.world import World

LockSource = Literal["beekeeper_notification_server", "unknown"]


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
        self.world.on_going_into_unlocked_mode()
        logger.info("Mode switched to UNLOCKED.")

    async def lock(self, source: LockSource = "unknown") -> None:
        self._is_unlocked = False
        await self.world.on_going_into_locked_mode(source)
        logger.info("Mode switched to LOCKED.")

    def __hash__(self) -> int:
        return id(self.world)
