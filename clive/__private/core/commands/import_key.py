from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.storage.mock_database import PrivateKeyAlias

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.storage.mock_database import PrivateKey


@dataclass
class ImportKey(Command[PrivateKeyAlias]):
    wallet: str
    key_to_import: PrivateKey
    beekeeper: Beekeeper

    def execute(self) -> None:
        self._result = PrivateKeyAlias(
            self.beekeeper.api.import_key(wallet_name=self.wallet, wif_key=self.key_to_import.key).public_key
        )
