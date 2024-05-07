import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.world_common_options import WorldWithoutBeekeeperCommonOptions

pending = CliveTyper(name="pending", help="Show operations in progress.")


@pending.command(name="withdrawals", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_pending_withdrawals(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Show pending withdrawals from savings initiated by transfer_from_savings operation."""
    from clive.__private.cli.commands.show.show_pending_withdrawals import ShowPendingWithdrawals

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowPendingWithdrawals(**common.as_dict(), account_name=account_name).run()


@pending.command(name="power-ups", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_pending_power_ups(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Vesting account balance is changed immediately after power up but it takes 1 month to affect governance voting power."""
    from clive.__private.cli.commands.show.show_pending_power_ups import ShowPendingPowerUps

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowPendingPowerUps(**common.as_dict(), account_name=account_name).run()


@pending.command(name="power-down", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_pending_power_down(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Power down takes place every week for 13 weeks after power down operation."""
    from clive.__private.cli.commands.show.show_pending_power_down import ShowPendingPowerDown

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowPendingPowerDown(**common.as_dict(), account_name=account_name).run()


@pending.command(name="removed-delegations", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_pending_removed_delegations(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """When a vesting shares delegation is removed, the delegated vesting shares are frozen for five days."""
    from clive.__private.cli.commands.show.show_pending_removed_delegations import ShowPendingRemovedDelegations

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowPendingRemovedDelegations(**common.as_dict(), account_name=account_name).run()
