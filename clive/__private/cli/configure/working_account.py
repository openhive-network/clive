from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import ProfileOptionsGroup, modified_param
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

working_account = CliveTyper(name="working-account", help="Manage your working account.")

_account_name_set_argument = typer.Argument(
    None,
    help=f"The name of the account to set as working. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@working_account.command(name="set", param_groups=[ProfileOptionsGroup])
async def set_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_set_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.configure.working_account import SetWorkingAccount

    common = ProfileOptionsGroup.get_instance()
    await SetWorkingAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


_account_name_remove_argument = modified_param(
    _account_name_set_argument, help=f"The name of the account to unset. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@working_account.command(name="unset", param_groups=[ProfileOptionsGroup])
async def unset_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = _account_name_remove_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.configure.working_account import UnsetWorkingAccount

    common = ProfileOptionsGroup.get_instance()
    await UnsetWorkingAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


_account_name_switch_argument = typer.Argument(
    None,
    help=f"The name of the account to switch to. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@working_account.command(name="switch", param_groups=[ProfileOptionsGroup])
async def switch_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = _account_name_switch_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Switch the working account."""
    from clive.__private.cli.commands.configure.working_account import SwitchWorkingAccount

    common = ProfileOptionsGroup.get_instance()
    await SwitchWorkingAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
