from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

if TYPE_CHECKING:
    from clive.__private.models import Asset

power_down = CliveTyper(name="power-down", help="Perform power-down, send withdraw_vesting_operation.")


@power_down.command(name="start", common_options=[OperationCommonOptions])
async def process_power_down_start(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.from_account_name_option,
    amount: str = options.voting_amount_option,
) -> None:
    """
    Start power down with given amount.

    If there is power down in progress displays error.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownStart

    common = OperationCommonOptions.get_instance()
    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDownStart(**common.as_dict(), account_name=account_name, amount=amount_)
    await operation.run()


@power_down.command(name="restart", common_options=[OperationCommonOptions])
async def process_power_down_restart(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.from_account_name_option,
    amount: str = options.voting_amount_option,
) -> None:
    """
    Restart power down with given amount.

    If there is power down in progress overrides it. If there is no power down in progress creates new.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown

    common = OperationCommonOptions.get_instance()
    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDown(**common.as_dict(), account_name=account_name, amount=amount_)
    await operation.run()


@power_down.command(name="cancel", common_options=[OperationCommonOptions])
async def process_power_down_cancel(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Stop power down by setting amount to 0."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownCancel

    common = OperationCommonOptions.get_instance()
    operation = ProcessPowerDownCancel(**common.as_dict(), account_name=account_name)
    await operation.run()
