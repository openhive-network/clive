from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli.beekeeper import beekeeper
from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import BeekeeperOptionsGroup, options
from clive.__private.cli.common.parameters import argument_related_options, arguments
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


@cli.command(param_groups=[BeekeeperOptionsGroup])
async def unlock(
    ctx: typer.Context,  # noqa: ARG001
    profile_name: Optional[str] = arguments.profile_name,
    profile_name_option: Optional[str] = argument_related_options.profile_name,
    password: str = options.password,
) -> None:
    """Unlock beekeeper session, session token must be set."""
    from clive.__private.cli.commands.main.unlock import CliveUnlock

    common = BeekeeperOptionsGroup.get_instance()
    profile_name_ = EnsureSingleProfileNameValue().of(profile_name, profile_name_option)
    await CliveUnlock(**common.as_dict(), profile_name=profile_name_, password=password).run()


@cli.command(param_groups=[BeekeeperOptionsGroup])
async def lock(
    ctx: typer.Context,  # noqa: ARG001
) -> None:
    """Lock all beekeeper sessions, session token must be set."""
    from clive.__private.cli.commands.main.lock import CliveLock

    common = BeekeeperOptionsGroup.get_instance()
    await CliveLock(**common.as_dict()).run()
