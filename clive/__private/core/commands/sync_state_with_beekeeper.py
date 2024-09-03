from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.profile import Profile

from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    profile: Profile
    beekeeper: Beekeeper
    app_state: AppState

    async def _execute(self) -> None:
        await self.__unlock_state_for_existing_session()

    async def __unlock_state_for_existing_session(self) -> None:
        if safe_settings.beekeeper.is_session_token_set:
            wallets_list = (await self.beekeeper.api.list_wallets()).wallets
            if self.profile.name in [wallet.name for wallet in wallets_list if wallet.unlocked]:
                self.app_state.unlock()
