from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.wallet_container import WalletContainer
    from clive.__private.core.world import World

LockSource = Literal["beekeeper_monitoring_thread", "unknown"]


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World
    _is_unlocked: bool = False
    """Holds info about the current state of the Clive application. Beekeeper can be in different state."""

    @property
    def is_unlocked(self) -> bool:
        return self._is_unlocked

    async def unlock(
        self,
        wallets: WalletContainer | None = None,
    ) -> None:
        if self._is_unlocked:
            return

        self._is_unlocked = True
        if wallets:
            await self.world.beekeeper_manager.set_wallets(wallets)
        self.world.on_going_into_unlocked_mode()
        logger.info("Mode switched to UNLOCKED.")

    def lock(self, source: LockSource = "unknown") -> None:
        if not self._is_unlocked:
            return

        self._is_unlocked = False
        self.world.beekeeper_manager.clear_wallets()
        self.world.on_going_into_locked_mode(source)
        logger.info("Mode switched to LOCKED.")

    def __hash__(self) -> int:
        return id(self.world)
