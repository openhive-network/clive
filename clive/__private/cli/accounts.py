import typer

from clive.__private.cli.common.with_profile import WithProfile

accounts = typer.Typer(name="accounts", help="Manage your working/watched account(s).")

working = typer.Typer(name="working", help="Manage your working account.")

accounts.add_typer(working)


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
