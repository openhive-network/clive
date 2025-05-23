from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

vote_witness = CliveTyper(name="vote-witness", help="Vote/unvote for a witness.")


@vote_witness.command(name="add")
async def process_vote_witness_add(
    account_name: str = options.account_name,
    witness_name: str = typer.Option(..., help="Witness name to vote."),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Vote for a witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness

    await ProcessVoteWitness(
        account_name=account_name,
        witness_name=witness_name,
        approve=True,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()


@vote_witness.command(name="remove")
async def process_vote_witness_remove(
    account_name: str = options.account_name,
    witness_name: str = typer.Option(..., help="Witness name to unvote."),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Unvote witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness

    await ProcessVoteWitness(
        account_name=account_name,
        witness_name=witness_name,
        approve=False,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
