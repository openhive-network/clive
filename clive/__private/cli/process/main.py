import typing
from enum import Enum
from functools import partial

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, TransferCommonOptions, options, update_authority
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.process.proxy import proxy
from clive.__private.cli.process.savings import savings
from clive.__private.cli.process.update_authority_common import get_update_authority_typer
from clive.__private.cli.process.vote_proposal import vote_proposal
from clive.__private.cli.process.vote_witness import vote_witness

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")

process.add_typer(proxy)
process.add_typer(savings)
process.add_typer(get_update_authority_typer("owner", update_authority.update_owner))
process.add_typer(get_update_authority_typer("active", update_authority.update_active))
process.add_typer(get_update_authority_typer("posting", update_authority.update_posting))
process.add_typer(vote_proposal)
process.add_typer(vote_witness)


@process.command(name="transfer", common_options=[OperationCommonOptions, TransferCommonOptions])
async def transfer(
    ctx: typer.Context,  # noqa: ARG001
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer

    operation_common = OperationCommonOptions.get_instance()
    transfer_common = TransferCommonOptions.get_instance()
    await Transfer(**operation_common.as_dict(), **transfer_common.as_dict(), to=to).run()


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
    await ProcessTransaction(
        **common.as_dict(),
        from_file=from_file,
        force_unsign=force_unsign,
        already_signed_mode=already_signed_mode,  # type: ignore [arg-type]
    ).run()


@process.command(name="update-memo-key", common_options=[OperationCommonOptions])
async def process_update_memo_key(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    memo_key: str = typer.Option(
        ...,
        "--key",
        help="New memo public key that will be set for account.",
        show_default=False,
    ),
) -> None:
    """Sets memo key."""
    from clive.__private.cli.commands.process.account_update import AccountUpdate

    update_memo_key_callback = partial(update_authority.set_memo_key, key=memo_key)

    common = OperationCommonOptions.get_instance()
    await AccountUpdate(
        **common.as_dict(), account_name=account_name, callbacks=[update_memo_key_callback], offline=True
    ).run()
