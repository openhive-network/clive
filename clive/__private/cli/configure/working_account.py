from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

working_account = CliveTyper(name="working-account", help="Manage your working account.")

_account_name_switch_argument = typer.Argument(
    None,
    help=f"The name of the account to switch to. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@working_account.command(name="switch")
async def switch_working_account(
    account_name: str = _account_name_switch_argument,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """
    Switch the working account.

    Args:
        account_name: The name of the account to switch to. This is required as an argument or option.
        account_name_option: An alternative way to specify the account name, if provided.

    Returns:
        None: This function does not return anything. It performs the action of switching the working account.
    """
    from clive.__private.cli.commands.configure.working_account import SwitchWorkingAccount

    await SwitchWorkingAccount(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()
