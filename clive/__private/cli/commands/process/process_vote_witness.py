from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import AccountWitnessVoteOperation


@dataclass(kw_only=True)
class ProcessVoteWitness(OperationCommand):
    """
    Class to vote for or against a witness.

    Args:
        account_name: The name of the account casting the vote.
        witness_name: The name of the witness to vote for or against.
        approve: True to approve the witness, False to disapprove.
    """

    account_name: str
    witness_name: str
    approve: bool

    async def _create_operation(self) -> AccountWitnessVoteOperation:
        """
        Create an operation to vote for or against a witness.

        Returns:
            AccountWitnessVoteOperation: The operation containing the vote details.
        """
        return AccountWitnessVoteOperation(
            account=self.account_name,
            witness=self.witness_name,
            approve=self.approve,
        )
