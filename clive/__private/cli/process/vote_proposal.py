from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.core.constants.node import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION

vote_proposal = CliveTyper(name="vote-proposal", help="Vote/unvote for a proposal.")

_proposal_id = typer.Option(
    ...,
    "--proposal-id",
    help=f"List of proposal identifiers, option can appear {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} times.",
)


@vote_proposal.command(name="add")
async def process_vote_proposal_add(
    account_name: str = options.account_name,
    proposal_id: list[int] = _proposal_id,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Vote for a proposal.

    Args:
        account_name: The name of the account casting the vote.
        proposal_id: List of proposal identifiers to vote for.
        sign: Optional signature for the transaction.
        broadcast: Whether to broadcast the transaction.
        save_file: Optional file to save the transaction data.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    await ProcessVoteProposal(
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=True,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()


@vote_proposal.command(name="remove")
async def process_vote_proposal_remove(
    account_name: str = options.account_name,
    proposal_id: list[int] = _proposal_id,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Unvote proposal.

    Args:
        account_name: The name of the account removing the vote.
        proposal_id: List of proposal identifiers to unvote.
        sign: Optional signature for the transaction.
        broadcast: Whether to broadcast the transaction.
        save_file: Optional file to save the transaction data.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    await ProcessVoteProposal(
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=False,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
