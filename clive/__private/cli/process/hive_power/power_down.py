from __future__ import annotations

from typing import TYPE_CHECKING, cast

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

power_down = CliveTyper(name="power-down", help="Perform power-down, send withdraw_vesting_operation.")


@power_down.command(name="start")
async def process_power_down_start(  # noqa: PLR0913
    account_name: str = options.from_account_name,
    amount: str = options.voting_amount,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Start power down with given amount.

    If there is power down in progress displays error.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownStart  # noqa: PLC0415

    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDownStart(
        account_name=account_name,
        amount=amount_,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    await operation.run()


@power_down.command(name="restart")
async def process_power_down_restart(  # noqa: PLR0913
    account_name: str = options.from_account_name,
    amount: str = options.voting_amount,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Restart power down with given amount.

    If there is power down in progress overrides it. If there is no power down in progress creates new.
    """
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown  # noqa: PLC0415

    amount_ = cast("Asset.Hive", amount)
    operation = ProcessPowerDown(
        account_name=account_name,
        amount=amount_,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    await operation.run()


@power_down.command(name="cancel")
async def process_power_down_cancel(
    account_name: str = options.account_name,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Stop power down by setting amount to 0."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDownCancel  # noqa: PLC0415

    operation = ProcessPowerDownCancel(
        account_name=account_name, sign_with=sign_with, broadcast=broadcast, save_file=save_file, autosign=autosign
    )
    await operation.run()
