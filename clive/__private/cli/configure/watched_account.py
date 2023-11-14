import typer

from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

watched_account = typer.Typer(name="watched-account", help="Manage your watched account(s).")


@watched_account.command(name="add")
@ProfileCommonOptions.decorator
async def add_watched_account(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the watched account to add.", show_default=False),
) -> None:
    """Add an account to the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import AddWatchedAccount

    common = ProfileCommonOptions(**ctx.params)
    await AddWatchedAccount(**common.dict(), account_name=account_name).run()


@watched_account.command(name="remove")
@ProfileCommonOptions.decorator
async def remove_watched_account(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the watched account to remove.", show_default=False),
) -> None:
    """Remove an account from the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import RemoveWatchedAccount

    common = ProfileCommonOptions(**ctx.params)
    await RemoveWatchedAccount(**common.dict(), account_name=account_name).run()
