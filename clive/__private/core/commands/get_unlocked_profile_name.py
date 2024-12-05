from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import MultipleProfilesUnlockedError, NoProfileUnlockedError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class GetUnlockedProfileName(CommandWithResult[str]):
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        wallets = (await self.beekeeper.api.list_wallets()).wallets
        unlocked = [wallet.name for wallet in wallets if wallet.unlocked]
        if len(unlocked) > 1:
            raise MultipleProfilesUnlockedError(self)
        if len(unlocked) < 1:
            raise NoProfileUnlockedError(self)
        self._result = unlocked[0]
