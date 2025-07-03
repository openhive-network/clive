from __future__ import annotations

import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.node import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION
from clive.__private.models.schemas import UpdateProposalVotesOperation


@dataclass(kw_only=True)
class ProcessVoteProposal(OperationCommand):
    """
    Class to handle voting on proposals.

    Args:
        account_name: The name of the account voting on the proposals.
        proposal_ids: A list of proposal IDs to vote on.
        approve: Whether to approve or disapprove the proposals.
    """

    account_name: str
    proposal_ids: list[int]
    approve: bool

    async def _create_operation(self) -> UpdateProposalVotesOperation:
        """
        Create an operation to update proposal votes.

        Returns:
            UpdateProposalVotesOperation: An operation object containing the voting details.
        """
        self.proposal_ids.sort()
        return UpdateProposalVotesOperation(
            voter=self.account_name,
            proposal_ids=self.proposal_ids,
            approve=self.approve,
            extensions=[],
        )

    async def validate(self) -> None:
        """
        Validate the command parameters before execution.

        Raises:
            CLIPrettyError: If the number of proposal IDs exceeds the maximum allowed.

        Returns:
            None
        """
        if len(self.proposal_ids) > MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION:
            raise CLIPrettyError(
                (
                    f"It's not allowed to have more than {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} ids in a"
                    " single operation"
                ),
                errno.E2BIG,
            )
        await super().validate()
