from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.models.transaction import Transaction


@dataclass(kw_only=True)
class UnSign(CommandWithResult[Transaction]):
    transaction: Transaction

    async def _execute(self) -> None:
        self.transaction.unsign()
        self._result = self.transaction
