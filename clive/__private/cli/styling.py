from __future__ import annotations

from typing import Final

STATUS_OK: Final[str] = "[green]{}[/green]"
STATUS_ERROR: Final[str] = "[red]{}[/red]"
STATUS_WARNING: Final[str] = "[orange1]{}[/orange1]"
STATUS_CONTENT_NOT_AVAILABLE: Final[str] = "[magenta]{}[/magenta]"


def colorize_ok(message: str) -> str:
    return STATUS_OK.format(message)


def colorize_error(message: str) -> str:
    return STATUS_ERROR.format(message)


def colorize_warning(message: str) -> str:
    return STATUS_WARNING.format(message)


def colorize_content_not_available(message: str) -> str:
    return STATUS_CONTENT_NOT_AVAILABLE.format(message)
