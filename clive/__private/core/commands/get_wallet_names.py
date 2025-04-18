from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked

if TYPE_CHECKING:
    from beekeepy import AsyncSession


type WalletStatus = Literal["all", "locked", "unlocked"]


@dataclass(kw_only=True)
class GetWalletNames(CommandWithResult[list[str]]):
    session: AsyncSession
    filter_by_status: WalletStatus = "all"

    async def _execute(self) -> None:
        wallets = await self.session.wallets
        if self.filter_by_status in ["locked", "unlocked"]:
            should_be_unlocked = self.filter_by_status == "unlocked"
            self._result = [
                wallet.name
                for wallet in wallets
                if await IsWalletUnlocked(wallet=wallet).execute_with_result() == should_be_unlocked
            ]
        else:
            self._result = [wallet.name for wallet in wallets]
