from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.keys.keys import PrivateKey, PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class ImportKey(CommandInActive, CommandWithResult[PublicKeyAliased]):
    wallet: str
    alias: str
    key_to_import: PrivateKey
    beekeeper: Beekeeper

    def _execute(self) -> None:
        imported = self.beekeeper.api.import_key(wallet_name=self.wallet, wif_key=self.key_to_import.value)
        self._result = PublicKeyAliased(alias=self.alias, value=imported.public_key)
