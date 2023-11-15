import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")


@process.command(name="transfer")
@OperationCommonOptions.decorator
async def transfer(
    ctx: typer.Context,
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer

    common = OperationCommonOptions(**ctx.params)
    await Transfer.from_(to=to, amount=amount, memo=memo, **common.dict()).run()
