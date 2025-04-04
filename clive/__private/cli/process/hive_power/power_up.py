from typing import TYPE_CHECKING, Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
    from clive.__private.models import Asset

power_up = CliveTyper(name="power-up", help="Perform power-up by sending transfer_to_vesting_operation.")


@power_up.callback(invoke_without_command=True)
async def process_power_up(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name,
    amount: str = typer.Option(
        ..., parser=hive_asset, help="The amount to transfer to vesting. (e.g. 2.500 HIVE)", show_default=False
    ),
    sign: Optional[str] = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: Optional[str] = options.save_file,
) -> None:
    """Perform power-up by sending transfer_to_vesting_operation."""
    from clive.__private.cli.commands.process.process_power_up import ProcessPowerUp

    amount_ = cast("Asset.Hive", amount)
    await ProcessPowerUp(
        from_account=from_account,
        to_account=to_account,
        amount=amount_,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()
