from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, cast, get_args

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.process.claim import claim
from clive.__private.cli.process.custom_operations.custom_json import custom_json
from clive.__private.cli.process.hive_power.delegations import delegations
from clive.__private.cli.process.hive_power.power_down import power_down
from clive.__private.cli.process.hive_power.power_up import power_up
from clive.__private.cli.process.hive_power.withdraw_routes import withdraw_routes
from clive.__private.cli.process.proxy import proxy
from clive.__private.cli.process.savings import savings
from clive.__private.cli.process.transfer_schedule import transfer_schedule
from clive.__private.cli.process.update_authority import get_update_authority_typer
from clive.__private.cli.process.vote_proposal import vote_proposal
from clive.__private.cli.process.vote_witness import vote_witness

if TYPE_CHECKING:
    from clive.__private.models import Asset

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")

process.add_typer(claim)
process.add_typer(proxy)
process.add_typer(savings)
process.add_typer(get_update_authority_typer("owner"))
process.add_typer(get_update_authority_typer("active"))
process.add_typer(get_update_authority_typer("posting"))
process.add_typer(vote_proposal)
process.add_typer(vote_witness)
process.add_typer(delegations)
process.add_typer(power_down)
process.add_typer(power_up)
process.add_typer(withdraw_routes)
process.add_typer(transfer_schedule)
process.add_typer(custom_json)


@process.command(name="transfer")
async def transfer(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer  # noqa: PLC0415

    amount_ = cast("Asset.LiquidT", amount)
    await Transfer(
        from_account=from_account,
        to=to,
        amount=amount_,
        memo=memo,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()


if is_tab_completion_active():
    AlreadySignedModeEnum = str
    ALREADY_SIGNED_MODE_DEFAULT = ""  # doesn't matter, won't be shown anyway
else:
    from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT
    from clive.__private.core.types import AlreadySignedMode

    # unfortunately typer doesn't support Literal types yet, so we have to convert it to an enum
    AlreadySignedModeEnum = Enum(  # type: ignore[misc, no-redef]
        "AlreadySignedModeEnum", {option: option for option in get_args(AlreadySignedMode)}
    )


@process.command(name="transaction")
async def process_transaction(  # noqa: PLR0913
    from_file: str = typer.Option(..., help="The file to load the transaction from.", show_default=False),
    force_unsign: bool = typer.Option(default=False, help="Whether to force unsigning the transaction."),  # noqa: FBT001
    already_signed_mode: AlreadySignedModeEnum = typer.Option(
        ALREADY_SIGNED_MODE_DEFAULT, help="How to handle the situation when transaction is already signed."
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """Process a transaction from file."""
    from clive.__private.cli.commands.process.process_transaction import ProcessTransaction  # noqa: PLC0415

    if isinstance(already_signed_mode, Enum):
        already_signed_mode = already_signed_mode.value

    await ProcessTransaction(
        from_file=from_file,
        force_unsign=force_unsign,
        already_signed_mode=already_signed_mode,  # type: ignore [arg-type]
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    ).run()


@process.command(name="update-memo-key")
async def process_update_memo_key(
    account_name: str = options.account_name,
    memo_key: str = typer.Option(
        ...,
        "--key",
        help="New memo public key that will be set for account.",
        show_default=False,
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Set memo key."""
    from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
        ProcessAccountUpdate,
        set_memo_key,
    )

    update_memo_key_callback = partial(set_memo_key, key=memo_key)

    operation = ProcessAccountUpdate(account_name=account_name, sign=sign, broadcast=broadcast, save_file=save_file)
    operation.add_callback(update_memo_key_callback)
    await operation.run()
