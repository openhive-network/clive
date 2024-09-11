import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

vote_proposal = CliveTyper(name="vote-proposal", help="Vote/unvote for a proposal.")


@vote_proposal.command(name="add", common_options=[OperationCommonOptions])
async def process_vote_proposal_add(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name,
    proposal_id: list[int] = options.proposal_id,
) -> None:
    """Vote for a proposal."""
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    common = OperationCommonOptions.get_instance()
    await ProcessVoteProposal(
        **common.as_dict(),
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=True,
    ).run()


@vote_proposal.command(name="remove", common_options=[OperationCommonOptions])
async def process_vote_proposal_remove(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name,
    proposal_id: list[int] = options.proposal_id,
) -> None:
    """Unvote proposal."""
    from clive.__private.cli.commands.process.process_vote_proposal import ProcessVoteProposal

    common = OperationCommonOptions.get_instance()
    await ProcessVoteProposal(
        **common.as_dict(),
        account_name=account_name,
        proposal_ids=proposal_id,
        approve=False,
    ).run()
