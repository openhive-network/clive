from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import ProfileOptionsGroup, argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

watched_account = CliveTyper(name="watched-account", help="Manage your watched account(s).")

_account_name_add_argument = typer.Argument(
    None, help=f"The name of the watched account to add. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False
)


@watched_account.command(name="add", param_groups=[ProfileOptionsGroup])
async def add_watched_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_add_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Add an account to the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import AddWatchedAccount

    common = ProfileOptionsGroup.get_instance()
    await AddWatchedAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


_account_name_remove_argument = modified_param(
    _account_name_add_argument, help=f"The name of the watched account to remove. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@watched_account.command(name="remove", param_groups=[ProfileOptionsGroup])
async def remove_watched_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_remove_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Remove an account from the watched accounts."""
    from clive.__private.cli.commands.configure.watched_account import RemoveWatchedAccount

    common = ProfileOptionsGroup.get_instance()
    await RemoveWatchedAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()
