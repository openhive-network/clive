import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

watched_account = CliveTyper(name="watched-account", help="Manage your watched account(s).")


@watched_account.command(name="add", common_options=[ProfileCommonOptions])
async def add_watched_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = typer.Option(..., help="The name of the watched account to add.", show_default=False),
) -> None:
    """Add an account to the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import AddWatchedAccount

    common = ProfileCommonOptions.get_instance()
    await AddWatchedAccount(**common.as_dict(), account_name=account_name).run()


@watched_account.command(name="remove", common_options=[ProfileCommonOptions])
async def remove_watched_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = typer.Option(..., help="The name of the watched account to remove.", show_default=False),
) -> None:
    """Remove an account from the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import RemoveWatchedAccount

    common = ProfileCommonOptions.get_instance()
    await RemoveWatchedAccount(**common.as_dict(), account_name=account_name).run()
