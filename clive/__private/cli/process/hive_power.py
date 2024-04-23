from decimal import Decimal

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options
from clive.models import Asset

power_down = CliveTyper(name="power-down", help="Perform power-down, send withdraw_vesting_operation.")
withdraw_routes = CliveTyper(name="withdraw-routes", help="Set or remove vesting withdraw routes.")
delegations = CliveTyper(name="delegations", help="Set or remove vesting delegaton.")


@power_down.command(name="start", common_options=[OperationCommonOptions])
async def process_power_down_start(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.from_account_name_option,
    amount: Asset.VotingT = options.voting_amount_option,
) -> None:
    """Start power down with given amount. If there is power down in progress displays error."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown

    common = OperationCommonOptions.get_instance()
    operation = ProcessPowerDown(**common.as_dict(), account_name=account_name, amount=amount, only_new_power_down=True)
    await operation.run()


@power_down.command(name="restart", common_options=[OperationCommonOptions])
async def process_power_down_restart(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.from_account_name_option,
    amount: Asset.VotingT = options.voting_amount_option,
) -> None:
    """Restart power down with given amount. If there is power down in progress overrides it. If there is no power down in progress creates new."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown

    common = OperationCommonOptions.get_instance()
    operation = ProcessPowerDown(**common.as_dict(), account_name=account_name, amount=amount)
    await operation.run()


@power_down.command(name="cancel", common_options=[OperationCommonOptions])
async def process_power_down_cancel(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Stops power down by setting amount to 0."""
    from clive.__private.cli.commands.process.process_power_down import ProcessPowerDown

    common = OperationCommonOptions.get_instance()
    operation = ProcessPowerDown(**common.as_dict(), account_name=account_name, amount=Asset.vests(0))
    await operation.run()


@withdraw_routes.command(name="set", common_options=[OperationCommonOptions])
async def process_withdraw_routes_set(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to_account: str = options.to_account_name_no_default_option,
    percent: float = typer.Option(
        ...,
        help="Route percent (0.00-100.00) for pair from_account and to_account.",
    ),
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
        **common.as_dict(),
        from_account=from_account,
        to_account=to_account,
        percent=Decimal.from_float(percent),
        auto_vest=auto_vest
    )
    await operation.run()


@withdraw_routes.command(name="remove", common_options=[OperationCommonOptions])
async def process_withdraw_routes_remove(
    ctx: typer.Context,  # noqa: ARG001
    from_account: str = options.from_account_name_option,
    to_account: str = options.to_account_name_no_default_option,
) -> None:
    """Clears withdraw route for pair of accounts "from" and "to"."""
    from clive.__private.cli.commands.process.process_withdraw_routes import ProcessWithdrawRoutes

    common = OperationCommonOptions.get_instance()
    operation = ProcessWithdrawRoutes(
        **common.as_dict(), from_account=from_account, to_account=to_account, percent=Decimal(0), auto_vest=False
    )
    await operation.run()


@delegations.command(name="set", common_options=[OperationCommonOptions])
async def process_delegations_set(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    delegatee: str = options.delegatee_account_name_option,
    amount: Asset.VotingT = options.voting_amount_option,
) -> None:
    """Adds or modifies vesting shares delegation for pair of accounts "account-name" and "delegatee"."""
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegations

    common = OperationCommonOptions.get_instance()
    operation = ProcessDelegations(**common.as_dict(), delegator=account_name, delegatee=delegatee, amount=amount)
    await operation.run()


@delegations.command(name="remove", common_options=[OperationCommonOptions])
async def process_delegations_remove(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    delegatee: str = options.delegatee_account_name_option,
) -> None:
    """Clears vesting shares delegation (by setting it to zero) for pair of accounts "account-name" and "delegatee"."""
    from clive.__private.cli.commands.process.process_delegations import ProcessDelegations

    common = OperationCommonOptions.get_instance()
    operation = ProcessDelegations(**common.as_dict(), delegator=account_name, delegatee=delegatee)
    await operation.run()
