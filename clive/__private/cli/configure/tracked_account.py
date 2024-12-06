from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup, argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

tracked_account = CliveTyper(name="tracked-account", help="Manage your tracked account(s).")

_account_name_add_argument = typer.Argument(
    None, help=f"The name of the tracked account to add. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False
)


@tracked_account.command(name="add", param_groups=[WorldOptionsGroup])
async def add_tracked_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_add_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Add an account to the tracked accounts."""
    from clive.__private.cli.commands.configure.tracked_account import AddTrackedAccount

    common = WorldOptionsGroup.get_instance()
    await AddTrackedAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


_account_name_remove_argument = modified_param(
    _account_name_add_argument, help=f"The name of the tracked account to remove. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@tracked_account.command(name="remove", param_groups=[WorldOptionsGroup])
async def remove_tracked_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_remove_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Remove an account from the tracked accounts."""
    from clive.__private.cli.commands.configure.tracked_account import RemoveTrackedAccount

    common = WorldOptionsGroup.get_instance()
    await RemoveTrackedAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
