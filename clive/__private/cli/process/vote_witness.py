from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

vote_witness = CliveTyper(name="vote-witness", help="Vote/unvote for a witness.")


@vote_witness.command(name="add")
async def process_vote_witness_add(  # noqa: PLR0913
    account_name: str = options.account_name,
    witness_name: str = typer.Option(..., help="Witness name to vote."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Vote for a witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness  # noqa: PLC0415

    await ProcessVoteWitness(
        account_name=account_name,
        witness_name=witness_name,
        approve=True,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@vote_witness.command(name="remove")
async def process_vote_witness_remove(  # noqa: PLR0913
    account_name: str = options.account_name,
    witness_name: str = typer.Option(..., help="Witness name to unvote."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Unvote witness."""
    from clive.__private.cli.commands.process.process_vote_witness import ProcessVoteWitness  # noqa: PLC0415

    await ProcessVoteWitness(
        account_name=account_name,
        witness_name=witness_name,
        approve=False,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
