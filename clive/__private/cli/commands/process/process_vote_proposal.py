from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations.update_proposal_votes_operation import UpdateProposalVotesOperation


@dataclass(kw_only=True)
class ProcessVoteProposal(OperationCommand):
    account_name: str
    proposal_id: int
    approve: bool

    async def _create_operation(self) -> UpdateProposalVotesOperation:
        return UpdateProposalVotesOperation(
            voter=self.account_name,
            proposal_ids=[self.proposal_id],
            approve=self.approve,
            extensions=[],
        )
