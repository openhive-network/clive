from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class ImportKey(CommandInUnlocked, CommandWithResult[PublicKeyAliased]):
    wallet: str
    key_to_import: PrivateKeyAliased
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        imported = await self.beekeeper.api.import_key(wallet_name=self.wallet, wif_key=self.key_to_import.value)
        self._result = PublicKeyAliased(alias=self.key_to_import.alias, value=imported.public_key)
