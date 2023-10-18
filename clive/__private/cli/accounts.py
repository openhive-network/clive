import typer

from clive.__private.cli.common.with_profile import WithProfile

accounts = typer.Typer(name="accounts", help="Manage your working/watched account(s).")

working = typer.Typer(name="working", help="Manage your working account.")
watched = typer.Typer(name="watched", help="Manage your watched account(s).")

accounts.add_typer(working)
accounts.add_typer(watched)


@accounts.command(name="list")
@WithProfile.decorator
async def list_(ctx: typer.Context) -> None:
    """List all accounts in the profile."""
    from clive.__private.cli.commands.accounts import AccountsList

    common = WithProfile(**ctx.params)
    await AccountsList(profile_data=common.profile_data).run()


@working.command(name="set")
@WithProfile.decorator
async def set_(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the account to set.", show_default=False),
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.accounts import AccountsWorkingSet

    common = WithProfile(**ctx.params)
    await AccountsWorkingSet(profile_data=common.profile_data, account_name=account_name).run()


@working.command()
@WithProfile.decorator
async def unset(
    ctx: typer.Context,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.accounts import AccountsWorkingUnset

    common = WithProfile(**ctx.params)
    await AccountsWorkingUnset(profile_data=common.profile_data).run()


@working.command()
@WithProfile.decorator
async def show(
    ctx: typer.Context,
) -> None:
    """Show the working account."""
    from clive.__private.cli.commands.accounts import AccountsWorkingShow

    common = WithProfile(**ctx.params)
    await AccountsWorkingShow(profile_data=common.profile_data).run()


@watched.command()
@WithProfile.decorator
async def add(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the watched account to add.", show_default=False),
) -> None:
    """Add an account to the watched accounts."""
    from clive.__private.cli.commands.accounts import AccountsWatchedAdd

    common = WithProfile(**ctx.params)
    await AccountsWatchedAdd(profile_data=common.profile_data, account_name=account_name).run()


@watched.command()
@WithProfile.decorator
async def remove(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the watched account to remove.", show_default=False),
) -> None:
    """Remove an account from the watched accounts."""
    from clive.__private.cli.commands.accounts import AccountsWatchedRemove

    common = WithProfile(**ctx.params)
    await AccountsWatchedRemove(profile_data=common.profile_data, account_name=account_name).run()


@watched.command(name="list")
@WithProfile.decorator
async def list_watched_accounts(
    ctx: typer.Context,
) -> None:
    """List all watched accounts in the profile."""
    from clive.__private.cli.commands.accounts import AccountsWatchedList

    common = WithProfile(**ctx.params)
    await AccountsWatchedList(profile_data=common.profile_data).run()
