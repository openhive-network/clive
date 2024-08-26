from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.aliased import AccountWitnessVoteOperation


@dataclass(kw_only=True)
class ProcessVoteWitness(OperationCommand):
    account_name: str
    witness_name: str
    approve: bool

    async def _create_operation(self) -> AccountWitnessVoteOperation:
        return AccountWitnessVoteOperation(
            account=self.account_name,
            witness=self.witness_name,
            approve=self.approve,
        )
