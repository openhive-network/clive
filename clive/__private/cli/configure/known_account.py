from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleAccountNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

known_account = CliveTyper(name="known-account", help="Manage your known account(s).")

_account_name_add_argument = typer.Argument(
    None, help=f"The name of the known account to add. ({REQUIRED_AS_ARG_OR_OPTION})", show_default=False
)


@known_account.command(name="add")
async def add_known_account(
    account_name: str | None = _account_name_add_argument,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Add an account to the list of known accounts."""
    from clive.__private.cli.commands.configure.known_account import AddKnownAccount

    await AddKnownAccount(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


_account_name_remove_argument = modified_param(
    _account_name_add_argument, help=f"The name of the known account to remove. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@known_account.command(name="remove")
async def remove_known_account(
    account_name: str | None = _account_name_remove_argument,
    account_name_option: str | None = argument_related_options.account_name,
) -> None:
    """Remove an account from the list of known accounts."""
    from clive.__private.cli.commands.configure.known_account import RemoveKnownAccount

    await RemoveKnownAccount(account_name=EnsureSingleAccountNameValue().of(account_name, account_name_option)).run()


@known_account.command(name="enable")
async def enable_known_accounts(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    CLI - If you want to broadcast an operation, you must first add the target account to the list of known accounts.
    TUI - The target account is added to the list of known accounts automatically after adding an operation to the cart.
    """  # noqa: D205
    from clive.__private.cli.commands.configure.known_account import EnableKnownAccounts

    await EnableKnownAccounts().run()


@known_account.command(name="disable")
async def disable_know_accounts(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    CLI - The target account is not checked if it is on the list of known accounts.
    TUI - The target account is not added to the list of known accounts automatically\
 after adding an operation to the cart.
    """  # noqa: D205
    from clive.__private.cli.commands.configure.known_account import DisableKnownAccounts

    await DisableKnownAccounts().run()
