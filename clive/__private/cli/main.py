from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli.beekeeper import beekeeper
from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import BeekeeperOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleProfileNameValue
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.configure.main import configure
from clive.__private.cli.process.main import process
from clive.__private.cli.show.main import show

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""
cli = CliveTyper(help=HELP)

cli.add_typer(configure)
cli.add_typer(show)
cli.add_typer(process)
cli.add_typer(beekeeper)

if not is_tab_completion_active():
    from clive.__private.cli.error_handlers import register_error_handlers

    register_error_handlers(cli)


@cli.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Show the current version and exit.", is_eager=True
    ),
) -> None:
    if version:
        from clive import __version__
        from clive.__private.storage.model import calculate_storage_model_revision

        typer.echo(f"Clive version: {__version__}\nStorage model revision: {calculate_storage_model_revision()}")


_profile_name_unlock_argument = typer.Argument(
    None,
    help="The name of the profile to unlock (can be selected interactively if not provided).",
    show_default=False,
)


@cli.command(name="unlock", param_groups=[BeekeeperOptionsGroup])
async def unlock(
    ctx: typer.Context,  # noqa: ARG001
    profile_name: Optional[str] = _profile_name_unlock_argument,
    profile_name_option: Optional[str] = argument_related_options.profile_name,
    unlock_time_mins: Optional[int] = typer.Option(
        None, "--unlock-time", help="Time to unlock the profile in minutes, default is no timeout.", show_default=False
    ),
    include_create_new_profile: bool = typer.Option(  # noqa: FBT001
        default=False,
        hidden=True,
    ),
) -> None:
    """
    Unlocks the selected profile.

    By default unlock is permanent and has no timeout.
    """
    from clive.__private.cli.commands.unlock import Unlock

    common = BeekeeperOptionsGroup.get_instance()
    await Unlock(
        **common.as_dict(),
        profile_name=EnsureSingleProfileNameValue().of(profile_name, profile_name_option, allow_none=True),
        unlock_time_mins=unlock_time_mins,
        include_create_new_profile=include_create_new_profile,
    ).run()


@cli.command(name="lock", param_groups=[BeekeeperOptionsGroup])
async def lock(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """
    Locks the profile.

    Locks all wallets in beekeeper session.
    """
    from clive.__private.cli.commands.lock import Lock

    common = BeekeeperOptionsGroup.get_instance()
    await Lock(**common.as_dict()).run()
