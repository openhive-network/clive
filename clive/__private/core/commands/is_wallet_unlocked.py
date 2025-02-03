from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy import AsyncWallet


@dataclass(kw_only=True)
class IsWalletUnlocked(CommandWithResult[bool]):
    """Check if the wallet with given name is unlocked on the beekeeper."""

    wallet: AsyncWallet

    async def _execute(self) -> None:
        is_wallet_unlocked = await self.wallet.unlocked is not None
        self._result = is_wallet_unlocked
