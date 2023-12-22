import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

vote_witness = CliveTyper(name="vote-witness", help="Vote/unvote for a witness.")


@vote_witness.command(name="add", common_options=[OperationCommonOptions])
async def process_vote_witness_add(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    witness_name: str = typer.Option(..., help="Witness name to vote."),
) -> None:
    """Vote for a witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness

    common = OperationCommonOptions.get_instance()
    await ProcessVoteWitness(
        **common.as_dict(),
        account_name=account_name,
        witness_name=witness_name,
        approve=True,
    ).run()


@vote_witness.command(name="remove", common_options=[OperationCommonOptions])
async def process_vote_witness_remove(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    witness_name: str = typer.Option(..., help="Witness name to unvote."),
) -> None:
    """Unvote witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness

    common = OperationCommonOptions.get_instance()
    await ProcessVoteWitness(
        **common.as_dict(),
        account_name=account_name,
        witness_name=witness_name,
        approve=False,
    ).run()
