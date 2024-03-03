from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased

if TYPE_CHECKING:
    from clive.models.aliased import UnlockedWallet


@dataclass(kw_only=True)
class ImportKey(CommandInActive, CommandWithResult[PublicKeyAliased]):
    key_to_import: PrivateKeyAliased
    wallet: UnlockedWallet

    async def _execute(self) -> None:
        imported = await self.wallet.import_key(private_key=self.key_to_import.value)
        self._result = PublicKeyAliased(alias=self.key_to_import.alias, value=imported)
