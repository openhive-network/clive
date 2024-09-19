from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationOptionsGroup, modified_param, options
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


@dataclass(kw_only=True)
class TransferScheduleCommonOptionsGroup(OperationOptionsGroup):
    from_account: str = options.from_account_name
    to: str = options.to_account_name_required


@transfer_schedule.command(name="create", param_groups=[TransferScheduleCommonOptionsGroup])
async def process_transfer_schedule_create(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    amount: str = options.liquid_amount,
    repeat: int = _repeat_value,
    frequency: timedelta = _frequency_value,
    memo: str = options.memo_value,
    pair_id: int = _pair_id_value,
) -> None:
    """Create a new recurrent transfer. First recurrent transfer will be sent immediately."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleCreate

    transfer_schedule_common = TransferScheduleCommonOptionsGroup.get_instance()

    await ProcessTransferScheduleCreate(
        **transfer_schedule_common.as_dict(),
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
    ).run()


@transfer_schedule.command(name="modify", param_groups=[TransferScheduleCommonOptionsGroup])
async def process_transfer_schedule_modify(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    amount: str = options.liquid_amount_optional,
    repeat: Optional[int] = _repeat_value_optional,
    frequency: Optional[timedelta] = _frequency_value_optional,
    memo: Optional[str] = options.memo_value_optional,
    pair_id: Optional[int] = _pair_id_value_none,
) -> None:
    """
    Modify an existing recurrent transfer.

    If you change the frequency, the first execution after modification is update date + frequency.
    """
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleModify

    transfer_schedule_common = TransferScheduleCommonOptionsGroup.get_instance()
    await ProcessTransferScheduleModify(
        **transfer_schedule_common.as_dict(),
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
    ).run()


@transfer_schedule.command(name="remove", param_groups=[TransferScheduleCommonOptionsGroup])
async def process_transfer_schedule_remove(
    ctx: typer.Context,  # noqa: ARG001
    pair_id: Optional[int] = _pair_id_value_none,
) -> None:
    """Remove an existing recurrent transfer."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleRemove

    transfer_schedule_common = TransferScheduleCommonOptionsGroup.get_instance()
    await ProcessTransferScheduleRemove(**transfer_schedule_common.as_dict(), pair_id=pair_id).run()
