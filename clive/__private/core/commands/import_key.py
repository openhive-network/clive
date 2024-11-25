from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased


@dataclass(kw_only=True)
class ImportKey(CommandInUnlocked, CommandWithResult[PublicKeyAliased]):
    key_to_import: PrivateKeyAliased

    async def _execute(self) -> None:
        imported = await self.unlocked_wallet.import_key(private_key=self.key_to_import.value)
        self._result = PublicKeyAliased(alias=self.key_to_import.alias, value=imported)
