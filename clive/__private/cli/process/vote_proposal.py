from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationOptionsGroup, options
from clive.__private.core.constants.node import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION

vote_proposal = CliveTyper(name="vote-proposal", help="Vote/unvote for a proposal.")

_proposal_id = typer.Option(
    ...,
    "--proposal-id",
    help=f"List of proposal identifiers, option can appear {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} times.",
)


@vote_proposal.command(name="add", param_groups=[OperationOptionsGroup])
async def process_vote_proposal_add(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name,
    proposal_id: list[int] = _proposal_id,
) -> None:
    """Vote for a proposal."""
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    common = OperationOptionsGroup.get_instance()
    await ProcessVoteProposal(
        **common.as_dict(),
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=True,
    ).run()


@vote_proposal.command(name="remove", param_groups=[OperationOptionsGroup])
async def process_vote_proposal_remove(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name,
    proposal_id: list[int] = _proposal_id,
) -> None:
    """Unvote proposal."""
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    common = OperationOptionsGroup.get_instance()
    await ProcessVoteProposal(
        **common.as_dict(),
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=False,
    ).run()
