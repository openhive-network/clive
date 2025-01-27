from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.models.schemas import FindProposals, Proposal

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class FindProposal(CommandWithResult[Proposal]):
    node: Node
    proposal_id: int

    async def _execute(self) -> None:
        response: FindProposals = await self.node.api.database_api.find_proposals(proposal_ids=[self.proposal_id])
        proposals_amount = len(response.proposals)
        assert (
            proposals_amount == 1
        ), f"Expected a single proposal to be found, while `{proposals_amount}` were received."
        first_proposal = response.proposals[0]
        assert (
            first_proposal.id_ == self.proposal_id
        ), f"Mismatch between expected proposal id `{first_proposal.id_}` and received one `{self.proposal_id}`."
        self._result = first_proposal
