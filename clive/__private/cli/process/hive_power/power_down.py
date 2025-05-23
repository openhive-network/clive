from __future__ import annotations

from typing import TYPE_CHECKING, cast

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models import Asset

power_down = CliveTyper(name="power-down", help="Perform power-down, send withdraw_vesting_operation.")


@power_down.command(name="start")
async def process_power_down_start(
    account_name: str = options.from_account_name,
    amount: str = options.voting_amount,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Start power down with given amount.

    If there is power down in progress displays error.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownStart

    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDownStart(
        account_name=account_name,
        amount=amount_,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    )
    await operation.run()


@power_down.command(name="restart")
async def process_power_down_restart(
    account_name: str = options.from_account_name,
    amount: str = options.voting_amount,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Restart power down with given amount.

    If there is power down in progress overrides it. If there is no power down in progress creates new.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown

    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDown(
        account_name=account_name, amount=amount_, sign=sign, broadcast=broadcast, save_file=save_file
    )
    await operation.run()


@power_down.command(name="cancel")
async def process_power_down_cancel(
    account_name: str = options.account_name,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Stop power down by setting amount to 0."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownCancel

    operation = ProcessPowerDownCancel(account_name=account_name, sign=sign, broadcast=broadcast, save_file=save_file)
    await operation.run()
