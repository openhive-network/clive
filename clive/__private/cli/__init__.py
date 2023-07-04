from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli.list import list_
from clive.__private.cli.spawn import spawn
from clive.__private.cli.transfer import transfer
from clive.__private.run_tui import run_tui
from clive.version import VERSION_INFO

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""  # fmt: skip

cli = typer.Typer(help=HELP, rich_markup_mode="rich", context_settings={"help_option_names": ["-h", "--help"]})

cli.add_typer(transfer, name="transfer")
cli.add_typer(list_, name="list")
cli.add_typer(spawn, name="spawn")


@cli.callback(invoke_without_command=True)
def _main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Show the current version and exit.", is_eager=True
    ),
) -> None:
    if version:
        typer.echo(f"CLIVE Version: {VERSION_INFO}")
        raise typer.Exit()


@cli.command()
def run() -> None:
    """Launch the TUI application."""
    run_tui()
