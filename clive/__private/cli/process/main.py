import typing
from enum import Enum

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions
from clive.__private.cli.completion import is_tab_completion_active

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


if is_tab_completion_active():
    AlreadySignedModeEnum = str
    ALREADY_SIGNED_MODE_DEFAULT = ""  # doesn't matter, won't be shown anyway
else:
    from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode

    # unfortunately typer doesn't support Literal types yet, so we have to convert it to an enum
    AlreadySignedModeEnum = Enum(  # type: ignore[misc, no-redef]
        "AlreadySignedModeEnum", {option: option for option in typing.get_args(AlreadySignedMode)}
    )


@process.command(name="transaction", common_options=[OperationCommonOptions])
async def process_transaction(
    ctx: typer.Context,  # noqa: ARG001
    from_file: str = typer.Option(..., help="The file to load the transaction from.", show_default=False),
    force_unsign: bool = typer.Option(False, help="Whether to force unsigning the transaction."),
    already_signed_mode: AlreadySignedModeEnum = typer.Option(
        ALREADY_SIGNED_MODE_DEFAULT, help="How to handle the situation when transaction is already signed."
    ),
) -> None:
    """Process a transaction from file."""
    from clive.__private.cli.commands.process.process_transaction import ProcessTransaction

    if isinstance(already_signed_mode, Enum):
        already_signed_mode = already_signed_mode.value

    common = OperationCommonOptions.get_instance()
    await ProcessTransaction.from_(
        **common.as_dict(), from_file=from_file, force_unsign=force_unsign, already_signed_mode=already_signed_mode
    ).run()
