from __future__ import annotations

from typing import Final

STATUS_OK: Final[str] = "[green]{}[/green]"
STATUS_ERROR: Final[str] = "[red]{}[/red]"
STATUS_WARNING: Final[str] = "[yellow]{}[/yellow]"
STATUS_CONTENT_NOT_AVAILABLE: Final[str] = "[magenta]{}[/magenta]"


def colorize_ok(message: str) -> str:
    """
    Colorizes a message in green to indicate success.

    Args:
        message: The message to be colorized.

    Returns:
        str: The colorized message.
    """
    return STATUS_OK.format(message)


def colorize_error(message: str) -> str:
    """
    Colorizes a message in red to indicate an error.

    Args:
        message: The message to be colorized.

    Returns:
        str: The colorized message.
    """
    return STATUS_ERROR.format(message)


def colorize_warning(message: str) -> str:
    """
    Colorizes a message in yellow to indicate a warning.

    Args:
        message: The message to be colorized.

    Returns:
        str: The colorized message.
    """
    return STATUS_WARNING.format(message)


def colorize_content_not_available(message: str) -> str:
    """
    Colorizes a message in magenta to indicate that content is not available.

    Args:
        message: The message to be colorized.

    Returns:
        str: The colorized message.
    """
    return STATUS_CONTENT_NOT_AVAILABLE.format(message)
