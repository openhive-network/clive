from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class ProcessVoteWitness(OperationCommand):
    account_name: str
    witness_name: str
    approve: bool

    async def _create_operations(self) -> ComposeTransaction:
        yield AccountWitnessVoteOperation(
            account=self.account_name,
            witness=self.witness_name,
            approve=self.approve,
        )
