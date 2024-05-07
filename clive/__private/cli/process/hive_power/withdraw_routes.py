from decimal import Decimal

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

withdraw_routes = CliveTyper(name="withdraw-routes", help="Set or remove vesting withdraw routes.")


@withdraw_routes.command(name="set", common_options=[OperationCommonOptions])
async def process_withdraw_routes_set(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to_account: str = options.to_account_name_no_default_option,
    percent: Decimal = options.percent_option,
    auto_vest: bool = typer.Option(
        False,
        help="If auto-vest is set, then the amount of the Hive is immediately converted into HP on the balance. "
        "With no-auto-vest there is no conversion from Hive into HP.",
    ),
) -> None:
    """Adds new withdraw route/modifies existing route for pair of accounts "from" and "to"."""
    from clive.__private.cli.commands.process.process_withdraw_routes import ProcessWithdrawRoutes

    common = OperationCommonOptions.get_instance()
    operation = ProcessWithdrawRoutes(
        **common.as_dict(), from_account=from_account, to_account=to_account, percent=percent, auto_vest=auto_vest
    )
    await operation.run()


@withdraw_routes.command(name="remove", common_options=[OperationCommonOptions])
async def process_withdraw_routes_remove(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to_account: str = options.to_account_name_no_default_option,
) -> None:
    """Clears withdraw route for pair of accounts "from" and "to"."""
    from clive.__private.cli.commands.process.process_withdraw_routes import ProcessWithdrawRoutesRemove

    common = OperationCommonOptions.get_instance()
    operation = ProcessWithdrawRoutesRemove(**common.as_dict(), from_account=from_account, to_account=to_account)
    await operation.run()
