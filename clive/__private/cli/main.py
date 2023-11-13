from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli.beekeeper import beekeeper
from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.configure.main import configure
from clive.__private.cli.process.main import process
from clive.__private.cli.profile import profile
from clive.__private.cli.show.main import show

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""
cli = CliveTyper(help=HELP, rich_markup_mode="rich", context_settings={"help_option_names": ["-h", "--help"]})

cli.add_typer(configure)
cli.add_typer(show)
cli.add_typer(process)
cli.add_typer(profile)
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

        typer.echo(f"CLIVE Version: {__version__}")
