from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.logger import logger

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.world import World

LockSource = Literal["beekeeper_monitoring_thread", "unknown"]


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World
    _previous_state: bool = False

    @property
    async def is_unlocked(self) -> bool:
        if not self.world._is_unlocked_wallet_set:
            return False
        return (await self.world._unlocked_wallet_ensure.unlocked) is not None

    async def unlock(self, unlocked_wallet: AsyncUnlockedWallet | None = None) -> None:
        if self._previous_state:
            return

        self._previous_state = True
        if unlocked_wallet:
            await self.world._set_unlocked_wallet(unlocked_wallet)
        self.world.on_going_into_unlocked_mode()
        logger.info("Mode switched to UNLOCKED.")

    def lock(self, source: LockSource = "unknown") -> None:
        if not self._previous_state:
            return

        self._previous_state = False
        self.world.on_going_into_locked_mode(source)
        logger.info("Mode switched to LOCKED.")

    def __hash__(self) -> int:
        return id(self.world)
