from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy.asynchronous import AsyncWallet


@dataclass(kw_only=True)
class IsWalletUnlocked(CommandWithResult[bool]):
    """
    Check if the wallet with given name is unlocked on the beekeeper.

    Attributes:
        wallet: The wallet to check.
    """

    wallet: AsyncWallet

    async def _execute(self) -> None:
        self._result = await self.wallet.is_unlocked()
