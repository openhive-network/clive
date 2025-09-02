from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from clive.__private.cli.styling import colorize_error, colorize_warning

if TYPE_CHECKING:
    from clive.__private.core.types import NotifyLevel


def print_info(message: str) -> None:
    notify(message, level="info")


def print_warning(message: str) -> None:
    prefix = "[b]Warning:[/] "
    notify(prefix + message, level="warning")


def print_error(message: str) -> None:
    prefix = "[b]Error:[/] "
    notify(prefix + message, level="error")


def notify(message: str, *, level: NotifyLevel = "info") -> None:
    if level == "warning":
        message = colorize_warning(message)
    elif level == "error":
        message = colorize_error(message)

    console = Console()
    console.print(message)
