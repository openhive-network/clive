import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions

working_account = CliveTyper(name="working-account", help="Manage your working account.")


@working_account.command(name="add", common_options=[ProfileCommonOptions])
async def add_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = typer.Option(..., help="The name of the account to set.", show_default=False),
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.configure.working_account import AddWorkingAccount

    common = ProfileCommonOptions.get_instance()
    await AddWorkingAccount(**common.as_dict(), account_name=account_name).run()


working_account_name_to_remove_option = options.modified_option(
    options.account_name_option, help="The name of the account to unset."
)


@working_account.command(name="remove", common_options=[ProfileCommonOptions])
async def remove_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = working_account_name_to_remove_option,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.configure.working_account import RemoveWorkingAccount

    common = ProfileCommonOptions.get_instance()
    await RemoveWorkingAccount(**common.as_dict(), account_name=account_name).run()
