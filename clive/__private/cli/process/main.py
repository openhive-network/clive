import typer

from clive.__private.cli.common.operation_common import OperationCommon

process = typer.Typer(name="process", help="Process something (e.g. perform a transfer).")


@process.command(name="transfer")
@OperationCommon.decorator
async def transfer(
    ctx: typer.Context,
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer

    common = OperationCommon(**ctx.params)
    await Transfer.from_(to=to, amount=amount, memo=memo, **common.dict()).run()