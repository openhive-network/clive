from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli.beekeeper import beekeeper
from clive.__private.cli.list import list_
from clive.__private.cli.transfer import transfer

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""

cli = typer.Typer(help=HELP, rich_markup_mode="rich", context_settings={"help_option_names": ["-h", "--help"]})

cli.add_typer(transfer, name="transfer")
cli.add_typer(list_, name="list")
cli.add_typer(beekeeper, name="beekeeper")


@cli.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Show the current version and exit.", is_eager=True
    ),
) -> None:
    if version:
        from clive import __version__

        typer.echo(f"CLIVE Version: {__version__}")
        raise typer.Exit
