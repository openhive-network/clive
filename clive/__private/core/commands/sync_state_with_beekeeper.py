from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.exceptions import WalletNotFoundError

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    profile: Profile
    beekeeper: Beekeeper
    app_state: AppState

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        wallets_in_beekeeper = (await self.beekeeper.api.list_created_wallets()).wallets
        clive_wallet_name = self.profile.name
        clive_wallet_details = next(
            (wallet for wallet in wallets_in_beekeeper if wallet.name == clive_wallet_name), None
        )

        if clive_wallet_details is None:
            raise WalletNotFoundError(self, wallet_name=clive_wallet_name)

        self.app_state.unlock() if clive_wallet_details.unlocked else await self.app_state.lock()
