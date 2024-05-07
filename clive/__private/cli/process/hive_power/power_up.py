from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
    from clive.models import Asset

power_up = CliveTyper(name="power-up", help="Perform power-up by sending transfer_to_vesting_operation.")


@power_up.callback(common_options=[OperationCommonOptions], invoke_without_command=True)
async def process_power_up(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to_account: str = options.to_account_name_option,
    amount: str = typer.Option(
        ..., parser=hive_asset, help="The amount to transfer to vesting. (e.g. 2.500 HIVE)", show_default=False
    ),
) -> None:
    """Perform power-up by sending transfer_to_vesting_operation."""
    from clive.__private.cli.commands.process.process_power_up import ProcessPowerUp

    common = OperationCommonOptions.get_instance()
    amount_ = cast("Asset.Hive", amount)
    await ProcessPowerUp(**common.as_dict(), from_account=from_account, to_account=to_account, amount=amount_).run()
