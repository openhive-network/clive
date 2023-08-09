from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import calculate_sig_digest
from clive.models import Signature, Transaction

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys import PublicKey


@dataclass(kw_only=True)
class Sign(CommandInActive, CommandWithResult[Transaction]):
    beekeeper: Beekeeper
    transaction: Transaction
    key: PublicKey
    chain_id: str

    async def _execute(self) -> None:
        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        result = await self.beekeeper.api.sign_digest(sig_digest=sig_digest, public_key=self.key.value)
        self.transaction.signatures = [Signature(result.signature)]
        self._result = self.transaction
