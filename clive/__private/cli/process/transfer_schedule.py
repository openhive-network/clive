from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, cast

import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.options import (
    frequency_value_option,
    frequency_value_optional_option,
    liquid_amount_option,
    liquid_amount_optional_option,
    memo_value_option,
    memo_value_optional_option,
    pair_id_value_none_option,
    pair_id_value_option,
    repeat_value_option,
    repeat_value_optional_option,
)

if TYPE_CHECKING:
    from clive.models import Asset
from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions


@dataclass(kw_only=True)
class TransferScheduleCommonOptions(OperationCommonOptions):
    from_account: str = options.from_account_name_option
    to: str = options.to_account_name_no_default_option


transfer_schedule = CliveTyper(name="transfer-schedule", help="Create, modify or remove recurrent transfer.")


@transfer_schedule.command(name="create", common_options=[TransferScheduleCommonOptions])
async def process_transfer_schedule_create(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    amount: str = liquid_amount_option,
    repeat: int = repeat_value_option,
    frequency: timedelta = frequency_value_option,
    memo: str = memo_value_option,
    pair_id: int = pair_id_value_option,
) -> None:
    """Create a new recurrent transfer. First recurrent transfer will be sent immediately."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleCreate

    transfer_schedule_common = TransferScheduleCommonOptions.get_instance()

    await ProcessTransferScheduleCreate(
        **transfer_schedule_common.as_dict(),
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
    ).run()


@transfer_schedule.command(name="modify", common_options=[TransferScheduleCommonOptions])
async def process_transfer_schedule_modify(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    amount: str = liquid_amount_optional_option,
    repeat: Optional[int] = repeat_value_optional_option,
    frequency: Optional[timedelta] = frequency_value_optional_option,
    memo: Optional[str] = memo_value_optional_option,
    pair_id: Optional[int] = pair_id_value_none_option,
) -> None:
    """
    Modify an existing recurrent transfer.

    If you change the frequency, the first execution after modification is update date + frequency.
    """
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleModify

    transfer_schedule_common = TransferScheduleCommonOptions.get_instance()
    await ProcessTransferScheduleModify(
        **transfer_schedule_common.as_dict(),
        amount=cast("Asset.LiquidT", amount),
        repeat=repeat,
        frequency=frequency,
        memo=memo,
        pair_id=pair_id,
    ).run()


@transfer_schedule.command(name="remove", common_options=[TransferScheduleCommonOptions])
async def process_transfer_schedule_remove(
    ctx: typer.Context,  # noqa: ARG001
    pair_id: Optional[int] = pair_id_value_none_option,
) -> None:
    """Remove an existing recurrent transfer."""
    from clive.__private.cli.commands.process.process_transfer_schedule import ProcessTransferScheduleRemove

    transfer_schedule_common = TransferScheduleCommonOptions.get_instance()
    await ProcessTransferScheduleRemove(**transfer_schedule_common.as_dict(), pair_id=pair_id).run()
