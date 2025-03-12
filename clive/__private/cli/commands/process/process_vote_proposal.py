from __future__ import annotations

import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.node import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION
from clive.__private.models.schemas import UpdateProposalVotesOperation


@dataclass(kw_only=True)
class ProcessVoteProposal(OperationCommand):
    account_name: str
    proposal_ids: list[int]
    approve: bool

    async def _create_operation(self) -> UpdateProposalVotesOperation:
        self.proposal_ids.sort()
        return UpdateProposalVotesOperation(
            voter=self.account_name,
            proposal_ids=[self.proposal_ids],  # type: ignore[list-item]
            approve=self.approve,
            extensions=[],
        )

    async def validate(self) -> None:
        if len(self.proposal_ids) > MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION:
            raise CLIPrettyError(
                (
                    f"It's not allowed to have more than {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} ids in a"
                    " single operation"
                ),
                errno.E2BIG,
            )
        await super().validate()
