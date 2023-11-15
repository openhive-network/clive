import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

working_account = CliveTyper(name="working-account", help="Manage your working account.")


@working_account.command(name="add")
@ProfileCommonOptions.decorator
async def add_working_account(
    ctx: typer.Context,
    account_name: str = typer.Option(..., help="The name of the account to set.", show_default=False),
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.configure.working_account import AddWorkingAccount

    common = ProfileCommonOptions(**ctx.params)
    await AddWorkingAccount(**common.dict(), account_name=account_name).run()


@working_account.command(name="remove")
@ProfileCommonOptions.decorator
async def remove_working_account(
    ctx: typer.Context,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.configure.working_account import RemoveWorkingAccount

    common = ProfileCommonOptions(**ctx.params)
    await RemoveWorkingAccount(**common.dict()).run()
