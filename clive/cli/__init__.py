from __future__ import annotations

from typing import Final

import typer

from clive.run_tui import run_tui

HELP: Final[str] = """
CLI tool for the Clive TUI application to interact with the [bold red]Hive[/bold red] blockchain :bee: \n
Type "clive <command> --help" to read more about a specific subcommand.
"""  # fmt: skip

cli = typer.Typer(help=HELP, rich_markup_mode="rich", context_settings={"help_option_names": ["-h", "--help"]})
mock = typer.Typer()

cli.add_typer(mock, name="mock", help="Just a mock subcommand to enable typer subcommands.")


@cli.command()
def run() -> None:
    """Launch the TUI application."""
    run_tui()
