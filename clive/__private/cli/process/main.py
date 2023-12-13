import typing
from enum import Enum

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, TransferCommonOptions, options
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.process.savings import savings
from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")

process.add_typer(savings)


@process.command(name="transfer", common_options=[OperationCommonOptions, TransferCommonOptions])
async def transfer(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer

    operation_common = OperationCommonOptions.get_instance()
    transfer_common = TransferCommonOptions.get_instance()
    await Transfer(**operation_common.as_dict(), **transfer_common.as_dict(), from_account=from_account, to=to).run()


if is_tab_completion_active():
    AlreadySignedModeEnum = AlreadySignedMode
else:
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
    await ProcessTransaction(
        **common.as_dict(),
        from_file=from_file,
        force_unsign=force_unsign,
        already_signed_mode=already_signed_mode,
    ).run()
