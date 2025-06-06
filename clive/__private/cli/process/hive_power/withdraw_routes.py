from __future__ import annotations

from decimal import Decimal  # noqa: TC003

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

withdraw_routes = CliveTyper(name="withdraw-routes", help="Set or remove vesting withdraw routes.")


@withdraw_routes.command(name="set")
async def process_withdraw_routes_set(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name_required,
    percent: Decimal = options.percent,
    auto_vest: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="If auto-vest is set, then the amount of the Hive is immediately converted into HP on the balance. "
        "With no-auto-vest there is no conversion from Hive into HP.",
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """Add new withdraw route/modify existing route for pair of accounts "from" and "to"."""
    from clive.__private.cli.commands.process.process_withdraw_routes import ProcessWithdrawRoutes

    operation = ProcessWithdrawRoutes(
        from_account=from_account,
        to_account=to_account,
        percent=percent,
        auto_vest=auto_vest,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
    )
    await operation.run()


@withdraw_routes.command(name="remove")
async def process_withdraw_routes_remove(
    from_account: str = options.from_account_name,
    to_account: str = options.to_account_name_required,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Clear withdraw route for pair of accounts "from" and "to"."""
    from clive.__private.cli.commands.process.process_withdraw_routes import ProcessWithdrawRoutesRemove

    operation = ProcessWithdrawRoutesRemove(
        from_account=from_account,
        to_account=to_account,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    )
    await operation.run()
