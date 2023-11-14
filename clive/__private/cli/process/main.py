import typer

from clive.__private.cli.common import PerformTransactionCommon
from clive.__private.cli.common.operation_common import OperationCommon
from clive.__private.cli.exceptions import CLIPrettyError

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

@process.command(name="transaction")
@PerformTransactionCommon.decorator
async def process_transaction(
    ctx: typer.Context,
    from_file: str = typer.Option(..., help="The file to load the transaction from."),
) -> None:
    """Process a transaction."""
    from clive.__private.cli.commands.process.process_transaction import ProcessTransaction

    print(ctx.params)

    common = PerformTransactionCommon(**ctx.params)
    await ProcessTransaction.from_(from_file=from_file, **common.dict()).run()
