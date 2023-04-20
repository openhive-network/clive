from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import cachetools

if TYPE_CHECKING:
    from clive.__private.core.world import World


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World

    @cachetools.cached(cache=cachetools.TTLCache(maxsize=1, ttl=1.0))
    def is_active(self) -> bool:
        wallets = self.world.beekeeper.api.list_wallets().wallets
        for wallet in wallets:
            if wallet.name == self.world.profile_data.name:
                return wallet.unlocked
        return False

    def __hash__(self) -> int:
        return id(self.world)
