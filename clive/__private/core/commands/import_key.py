from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.storage.mock_database import PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.storage.mock_database import PrivateKey


@dataclass(kw_only=True)
class ImportKey(CommandInActive[PublicKeyAliased]):
    wallet: str
    alias: str
    key_to_import: PrivateKey
    beekeeper: Beekeeper

    _is_armed: bool = field(init=False, default=True)  # nothing to set here, the command is always armed

    def _execute(self) -> None:
        imported = self.beekeeper.api.import_key(wallet_name=self.wallet, wif_key=self.key_to_import.value)
        self._result = PublicKeyAliased(alias=self.alias, value=imported.public_key)
