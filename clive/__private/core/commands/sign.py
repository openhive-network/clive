from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.mockcpp import calculate_digest
from clive.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperRemote
    from clive.__private.storage.mock_database import PrivateKeyAlias


@dataclass
class Sign(Command[Transaction]):
    beekeeper: BeekeeperRemote
    transaction: Transaction
    key: PrivateKeyAlias

    def execute(self) -> None:
        self.transaction.transaction_id = calculate_digest(self.transaction)
        result = self.beekeeper.api.sign_digest(digest=self.transaction.transaction_id, public_key=self.key.key_name)
        self.transaction.signatures = [result.signature]
        self._result = self.transaction
