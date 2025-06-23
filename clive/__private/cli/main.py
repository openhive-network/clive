from __future__ import annotations

from typing import Final

import typer

from clive.__private.cli.beekeeper import beekeeper
from clive.__private.cli.clive_typer import CliveTyper
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
    version: bool | None = typer.Option(
        None, "--version", "-V", help="Show the current version and exit.", is_eager=True
    ),
) -> None:
    if version:
        from clive import __version__  # noqa: PLC0415
        from clive.__private.storage.storage_history import StorageHistory  # noqa: PLC0415

        typer.echo(f"Clive version: {__version__}")
        typer.echo(f"Storage model revision: {StorageHistory.get_latest_revision()}")
        typer.echo(f"Storage model version: {StorageHistory.get_latest_version()}")


_profile_name_unlock_argument = typer.Argument(
    None,
    help="The name of the profile to unlock (can be selected interactively if not provided).",
    show_default=False,
)


@cli.command(name="unlock")
async def unlock(
    profile_name: str | None = _profile_name_unlock_argument,
    profile_name_option: str | None = argument_related_options.profile_name,
    unlock_time_mins: int | None = typer.Option(
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
    from clive.__private.cli.commands.unlock import Unlock  # noqa: PLC0415

    await Unlock(
        profile_name=EnsureSingleProfileNameValue().of(profile_name, profile_name_option, allow_none=True),
        unlock_time_mins=unlock_time_mins,
        include_create_new_profile=include_create_new_profile,
    ).run()


@cli.command(name="lock")
async def lock() -> None:
    """
    Locks the profile.

    Locks all wallets in beekeeper session.
    """
    from clive.__private.cli.commands.lock import Lock  # noqa: PLC0415

    await Lock().run()


@cli.command(name="init", hidden=True)
async def init() -> None:
    """Initialize Clive environment and configuration."""
    from clive.__private.cli.commands.init import Init  # noqa: PLC0415

    await Init().run()
