from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from clive.__private.cli.styling import colorize_error, colorize_warning

if TYPE_CHECKING:
    from clive.__private.core.types import NotifyLevel


def notify(message: str, *, level: NotifyLevel = "info") -> None:
    """
    Print a notification message to the console with appropriate styling based on the level (warning/error).

    Args:
        message: The message to be printed.
        level: The level of the notification. Can be "info", "warning", or "error".

    Returns:
        None: This function does not return any value. It prints the message directly to the console.
    """
    if level == "warning":
        message = colorize_warning(message)
    elif level == "error":
        message = colorize_error(message)

    console = Console()
    console.print(message)
