from __future__ import annotations

from typing import Final

import typer

from clive.cli import style
from clive.run_tui import run_tui

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""  # fmt: skip

cli = typer.Typer(help=HELP, rich_markup_mode="rich", context_settings={"help_option_names": ["-h", "--help"]})
cli.add_typer(style.app, name="style", help="Manage styles for the Clive TUI application. :sparkles:")


@cli.command()
def run() -> None:
    """Launch the TUI application."""
    run_tui()
