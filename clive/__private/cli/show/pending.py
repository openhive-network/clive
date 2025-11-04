from __future__ import annotations

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options, arguments
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue

pending = CliveTyper(name="pending", help="Show operations in progress.")


@pending.command(name="withdrawals")
async def show_pending_withdrawals(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Show pending withdrawals from savings initiated by transfer_from_savings operation."""
    from clive.__private.cli.commands.show.show_pending_withdrawals import ShowPendingWithdrawals  # noqa: PLC0415

    await ShowPendingWithdrawals(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="power-ups")
async def show_pending_power_ups(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Vesting account balance is changed immediately after power up but it takes 1 month to affect governance voting power."""  # noqa: E501
    from clive.__private.cli.commands.show.show_pending_power_ups import ShowPendingPowerUps  # noqa: PLC0415

    await ShowPendingPowerUps(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@pending.command(name="power-down")
async def show_pending_power_down(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Power down takes place every week for 13 weeks after power down operation."""
    from clive.__private.cli.commands.show.show_pending_power_down import ShowPendingPowerDown  # noqa: PLC0415

    await ShowPendingPowerDown(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@pending.command(name="removed-delegations")
async def show_pending_removed_delegations(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """When a vesting shares delegation is removed, the delegated vesting shares are frozen for five days."""
    from clive.__private.cli.commands.show.show_pending_removed_delegations import (  # noqa: PLC0415
        ShowPendingRemovedDelegations,
    )

    await ShowPendingRemovedDelegations(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@pending.command(name="change-recovery-account")
async def show_pending_change_recovery_account(
    account_name: str = arguments.account_name,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    The change of the recovery account takes effect after the 30-day delay.

    During this period you can cancel change by sending another operation with previous recovery account name.
    """
    from clive.__private.cli.commands.show.show_pending_change_recovery_account import (  # noqa: PLC0415
        ShowPendingChangeRecoveryAccount,
    )

    await ShowPendingChangeRecoveryAccount(
        account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
