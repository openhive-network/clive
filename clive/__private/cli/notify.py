from rich.console import Console

from clive.__private.cli.styling import colorize_error, colorize_warning
from clive.__private.core.types import NotifyLevel


def notify(message: str, *, level: NotifyLevel = "info") -> None:
    if level == "warning":
        message = colorize_warning(message)
    elif level == "error":
        message = colorize_error(message)

    console = Console()
    console.print(message)
