from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.commands.update_node_data import DynamicGlobalPropertiesT
    from clive.__private.core.world import World


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World
    _dynamic_global_properties: DynamicGlobalPropertiesT | None = None

    def get_dynamic_global_properties(self) -> DynamicGlobalPropertiesT:
        if self._dynamic_global_properties is None:
            self.world.commands.update_node_data().raise_if_error_occurred()
        assert self._dynamic_global_properties is not None
        return self._dynamic_global_properties

    def is_active(self) -> bool:
        wallets = self.world.beekeeper.api.list_wallets().wallets
        for wallet in wallets:
            if wallet.name == self.world.profile_data.name:
                return wallet.unlocked
        return False

    def __hash__(self) -> int:
        return id(self.world)
