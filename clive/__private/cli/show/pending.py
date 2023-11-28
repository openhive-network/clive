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
    from clive.__private.cli.commands.show.show_pending import ShowPendingWithdrawals

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowPendingWithdrawals(**common.as_dict(), account_name=account_name).run()
