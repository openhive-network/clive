import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")


@process.command(name="transfer", common_options=[OperationCommonOptions])
async def transfer(
    ctx: typer.Context,  # noqa: ARG001
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer

    common = OperationCommonOptions.get_instance()
    await Transfer.from_(**common.as_dict(), to=to, amount=amount, memo=memo).run()


@process.command(name="transaction", common_options=[OperationCommonOptions])
async def process_transaction(
    ctx: typer.Context,  # noqa: ARG001
    from_file: str = typer.Option(..., help="The file to load the transaction from.", show_default=False),
    force_unsign: bool = typer.Option(False, help="Whether to force unsigning the transaction."),
) -> None:
    """Process a transaction from file."""
    from clive.__private.cli.commands.process.process_transaction import ProcessTransaction

    common = OperationCommonOptions.get_instance()
    await ProcessTransaction.from_(**common.as_dict(), from_file=from_file, force_unsign=force_unsign).run()
