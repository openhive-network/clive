from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import modified_param
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import ensure_single_value_account_name
from clive.__private.cli.common.profile_common_options import ProfileCommonOptions
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

working_account = CliveTyper(name="working-account", help="Manage your working account.")

_account_name_set_argument = typer.Argument(
    None,
    help=f"The name of the account to set as working. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@working_account.command(name="set", common_options=[ProfileCommonOptions])
async def set_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_set_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Set the working account."""
    from clive.__private.cli.commands.configure.working_account import SetWorkingAccount

    common = ProfileCommonOptions.get_instance()
    await SetWorkingAccount(
        **common.as_dict(), account_name=ensure_single_value_account_name(account_name, account_name_option)
    ).run()


_account_name_remove_argument = modified_param(
    _account_name_set_argument, help=f"The name of the account to unset. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@working_account.command(name="unset", common_options=[ProfileCommonOptions])
async def unset_working_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = _account_name_remove_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Unset the working account."""
    from clive.__private.cli.commands.configure.working_account import UnsetWorkingAccount

    common = ProfileCommonOptions.get_instance()
    await UnsetWorkingAccount(
        **common.as_dict(), account_name=ensure_single_value_account_name(account_name, account_name_option)
    ).run()
