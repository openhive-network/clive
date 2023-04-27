from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.world import World


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World

    def is_active(self) -> bool:
        wallets = self.world.beekeeper.api.list_wallets().wallets
        for wallet in wallets:
            if wallet.name == self.world.profile_data.name:
                return wallet.unlocked
        return False

    def __hash__(self) -> int:
        return id(self.world)
