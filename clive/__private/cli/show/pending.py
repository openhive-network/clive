from __future__ import annotations

from typing import TYPE_CHECKING

import typer  # noqa: TCH002

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options, arguments
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue

pending = CliveTyper(name="pending", help="Show operations in progress.")


@pending.command(name="withdrawals")
async def show_pending_withdrawals(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Show pending withdrawals from savings initiated by transfer_from_savings operation."""
    from clive.__private.cli.commands.show.show_pending_withdrawals import ShowPendingWithdrawals

    await ShowPendingWithdrawals(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="power-ups")
async def show_pending_power_ups(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Vesting account balance is changed immediately after power up but it takes 1 month to affect governance voting power."""  # noqa: E501
    from clive.__private.cli.commands.show.show_pending_power_ups import ShowPendingPowerUps

    await ShowPendingPowerUps(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@pending.command(name="power-down")
async def show_pending_power_down(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Power down takes place every week for 13 weeks after power down operation."""
    from clive.__private.cli.commands.show.show_pending_power_down import ShowPendingPowerDown

    await ShowPendingPowerDown(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@pending.command(name="removed-delegations")
async def show_pending_removed_delegations(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """When a vesting shares delegation is removed, the delegated vesting shares are frozen for five days."""
    from clive.__private.cli.commands.show.show_pending_removed_delegations import ShowPendingRemovedDelegations

    await ShowPendingRemovedDelegations(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
