import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions
from clive.__private.cli.common.world_common_options import WorldWithoutBeekeeperCommonOptions

show = CliveTyper(name="show", help="Show various data.")


@show.command("profiles")
async def show_profiles() -> None:
    """Show all stored profiles."""
    from clive.__private.cli.commands.show.show_profiles import ShowProfiles

    await ShowProfiles().run()


@show.command(name="profile", common_options=[ProfileCommonOptions])
async def show_profile(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show profile information."""
    from clive.__private.cli.commands.show.show_profile import ShowProfile

    common = ProfileCommonOptions.get_instance()
    await ShowProfile(**common.as_dict()).run()


@show.command(name="accounts", common_options=[ProfileCommonOptions])
async def show_accounts(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all accounts stored in the profile."""
    from clive.__private.cli.commands.show.show_accounts import ShowAccounts

    common = ProfileCommonOptions.get_instance()
    await ShowAccounts(**common.as_dict()).run()


@show.command(name="keys", common_options=[ProfileCommonOptions])
async def show_keys(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show all the public keys stored in Clive."""
    from clive.__private.cli.commands.show.show_keys import ShowKeys

    common = ProfileCommonOptions.get_instance()
    await ShowKeys(**common.as_dict()).run()


@show.command(name="balances", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_balances(ctx: typer.Context, account_name: str = options.account_name_option) -> None:  # noqa: ARG001
    """Show balances of the selected account."""
    from clive.__private.cli.commands.show.show_balances import ShowBalances

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowBalances(**common.as_dict(), account_name=account_name).run()


@show.command(name="node", common_options=[ProfileCommonOptions])
async def show_node(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show address of the currently selected node."""
    from clive.__private.cli.commands.show.show_node import ShowNode

    common = ProfileCommonOptions.get_instance()
    await ShowNode(**common.as_dict()).run()


@show.command(name="transaction-status", common_options=[WorldWithoutBeekeeperCommonOptions])
async def show_transaction_status(
    ctx: typer.Context,  # noqa: ARG001
    transaction_id: str = typer.Option(..., help="Hash of the transaction.", show_default=False),
) -> None:
    """Print status of a specific transaction."""
    from clive.__private.cli.commands.show.show_transaction_status import ShowTransactionStatus

    common = WorldWithoutBeekeeperCommonOptions.get_instance()
    await ShowTransactionStatus(**common.as_dict(), transaction_id=transaction_id).run()
