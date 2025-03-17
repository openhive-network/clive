from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup, argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

known_account = CliveTyper(name="known-account", help="Manage your known account(s).")

_account_name_add_argument = typer.Argument(
    None, help=f"The name of the known account to add. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False
)


@known_account.command(name="add", param_groups=[WorldOptionsGroup])
async def add_known_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_add_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Add an account to the list of known accounts."""
    from clive.__private.cli.commands.configure.known_account import AddKnownAccount

    common = WorldOptionsGroup.get_instance()
    await AddKnownAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


_account_name_remove_argument = modified_param(
    _account_name_add_argument, help=f"The name of the known account to remove. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@known_account.command(name="remove", param_groups=[WorldOptionsGroup])
async def remove_known_account(
    ctx: typer.Context,  # noqa: ARG001
    account_name: Optional[str] = _account_name_remove_argument,
    account_name_option: Optional[str] = argument_related_options.account_name,
) -> None:
    """Remove an account from the list of known accounts."""
    from clive.__private.cli.commands.configure.known_account import RemoveKnownAccount

    common = WorldOptionsGroup.get_instance()
    await RemoveKnownAccount(
        **common.as_dict(), account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)
    ).run()


@known_account.command(name="enable", param_groups=[WorldOptionsGroup])
async def enable_known_accounts(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    CLI - If you want to broadcast an operation, you must first add the target account to the list of known accounts.
    TUI - The target account is added to the list of known accounts automatically after broadcasting the transaction.
    """  # noqa: D205
    from clive.__private.cli.commands.configure.known_account import EnableKnownAccounts

    common = WorldOptionsGroup.get_instance()
    await EnableKnownAccounts(**common.as_dict()).run()


@known_account.command(name="disable", param_groups=[WorldOptionsGroup])
async def disable_know_accounts(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    CLI - The target account is not checked if it is on the list of known accounts.
    TUI - The target account is not added to the list of known accounts automatically after broadcasting the transaction.
    """  # noqa: D205, E501
    from clive.__private.cli.commands.configure.known_account import DisableKnownAccounts

    common = WorldOptionsGroup.get_instance()
    await DisableKnownAccounts(**common.as_dict()).run()
