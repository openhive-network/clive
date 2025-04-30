from __future__ import annotations

from datetime import timedelta  # noqa: TC003
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import modified_param, options
from clive.__private.cli.common.parsers import scheduled_transfer_frequency_parser
from clive.__private.core.constants.node import (
    SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
)
from clive.__private.core.shorthand_timedelta import SHORTHAND_TIMEDELTA_EXAMPLE

if TYPE_CHECKING:
    from clive.__private.models import Asset

transfer_schedule = CliveTyper(name="transfer-schedule", help="Create, modify or remove recurrent transfer.")

_frequency_value = typer.Option(
    ...,
    "--frequency",
    parser=scheduled_transfer_frequency_parser,
    help=f"How often the transfer should be executed ({SHORTHAND_TIMEDELTA_EXAMPLE})",
    show_default=False,
)

_frequency_value_optional = modified_param(_frequency_value, default=None)

_pair_id_value = typer.Option(
    0,
    "--pair-id",
    min=SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    help=(
        "Unique pair id used to differentiate between multiple transfers to the same account \n"
        "(will be mandatory since HF28)."
    ),
    show_default=True,
)

_pair_id_value_none = modified_param(_pair_id_value, default=None, show_default=False)


_repeat_value = typer.Option(
    ...,
    "--repeat",
    min=SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
    help="How many times the recurrent transfer should be executed. (must be greater than 1)",
    show_default=False,
)

_repeat_value_optional = modified_param(_repeat_value, default=None)


@transfer_schedule.command(name="create")
async def process_transfer_schedule_create(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = options.to_account_name_required,
    amount: str = options.liquid_amount,
    repeat: int = _repeat_value,
    frequency: timedelta = _frequency_value,
    memo: str = options.memo_value,
    pair_id: int = _pair_id_value,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """Create a new recurrent transfer. First recurrent transfer will be sent immediately."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleCreate

    await ProcessTransferScheduleCreate(
        from_account=from_account,
        to=to,
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    ).run()


@transfer_schedule.command(name="modify")
async def process_transfer_schedule_modify(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = options.to_account_name_required,
    amount: str = options.liquid_amount_optional,
    repeat: int | None = _repeat_value_optional,
    frequency: timedelta | None = _frequency_value_optional,
    memo: str | None = options.memo_value_optional,
    pair_id: int | None = _pair_id_value_none,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """
    Modify an existing recurrent transfer.

    If you change the frequency, the first execution after modification is update date + frequency.
    """
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleModify

    await ProcessTransferScheduleModify(
        from_account=from_account,
        to=to,
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    ).run()


@transfer_schedule.command(name="remove")
async def process_transfer_schedule_remove(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = options.to_account_name_required,
    pair_id: int | None = _pair_id_value_none,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Remove an existing recurrent transfer."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleRemove

    await ProcessTransferScheduleRemove(
        from_account=from_account,
        to=to,
        pair_id=pair_id,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
