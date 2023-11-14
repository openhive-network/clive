import typer

from clive.__private.cli.common.with_profile import WithProfile

working_account = typer.Typer(name="working-account", help="Manage your working account.")


@working_account.command(name="add")
@WithProfile.decorator
async def add_working_account(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the account to set.", show_default=False),
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.configure.working_account import AddWorkingAccount

    common = WithProfile(**ctx.params)
    await AddWorkingAccount(**common.dict(), account_name=account_name).run()


@working_account.command(name="remove")
@WithProfile.decorator
async def remove_working_account(
    ctx: typer.Context,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.configure.working_account import RemoveWorkingAccount

    common = WithProfile(**ctx.params)
    await RemoveWorkingAccount(**common.dict()).run()
