from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


WalletStatus: TypeAlias = Literal["all", "locked", "unlocked"]


@dataclass(kw_only=True)
class GetWalletNames(CommandWithResult[list[str]]):
    beekeeper: Beekeeper
    filter_by_status: WalletStatus = "all"

    async def _execute(self) -> None:
        wallets = (await self.beekeeper.api.list_wallets()).wallets
        if self.filter_by_status in ["locked", "unlocked"]:
            unlocked = self.filter_by_status == "unlocked"
            self._result = [wallet.name for wallet in wallets if wallet.unlocked == unlocked]
        else:
            self._result = [wallet.name for wallet in wallets]
