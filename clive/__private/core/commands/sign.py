from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.core.iwax import calculate_digest
from clive.models import Signature, Transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.storage.mock_database import PrivateKeyAlias


@dataclass
class Sign(Command[Transaction]):
    beekeeper: Beekeeper
    transaction: Transaction
    key: PrivateKeyAlias
    chain_id: str

    def execute(self) -> None:
        sig_digest = calculate_digest(self.transaction, self.chain_id)
        result = self.beekeeper.api.sign_digest(sig_digest=sig_digest, public_key=self.key.alias)
        self.transaction.signatures = [Signature(result.signature)]
        self._result = self.transaction
