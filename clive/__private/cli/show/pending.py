from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options, arguments
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue

pending = CliveTyper(name="pending", help="Show operations in progress.")


@pending.command(name="withdrawals", param_groups=[WorldOptionsGroup])
async def show_pending_withdrawals(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Show pending withdrawals from savings initiated by transfer_from_savings operation."""
    from clive.__private.cli.commands.show.show_pending_withdrawals import ShowPendingWithdrawals

    common = WorldOptionsGroup.get_instance()
    await ShowPendingWithdrawals(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="power-ups", param_groups=[WorldOptionsGroup])
async def show_pending_power_ups(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Vesting account balance is changed immediately after power up but it takes 1 month to affect governance voting power."""  # noqa: E501
    from clive.__private.cli.commands.show.show_pending_power_ups import ShowPendingPowerUps

    common = WorldOptionsGroup.get_instance()
    await ShowPendingPowerUps(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="power-down", param_groups=[WorldOptionsGroup])
async def show_pending_power_down(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Power down takes place every week for 13 weeks after power down operation."""
    from clive.__private.cli.commands.show.show_pending_power_down import ShowPendingPowerDown

    common = WorldOptionsGroup.get_instance()
    await ShowPendingPowerDown(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="removed-delegations", param_groups=[WorldOptionsGroup])
async def show_pending_removed_delegations(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """When a vesting shares delegation is removed, the delegated vesting shares are frozen for five days."""
    from clive.__private.cli.commands.show.show_pending_removed_delegations import ShowPendingRemovedDelegations

    common = WorldOptionsGroup.get_instance()
    await ShowPendingRemovedDelegations(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
