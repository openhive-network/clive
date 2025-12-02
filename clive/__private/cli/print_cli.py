from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from clive.__private.cli.styling import colorize_content_not_available, colorize_error, colorize_ok, colorize_warning

if TYPE_CHECKING:
    from rich.console import RenderableType


def print_cli(message: RenderableType, *, console: Console | None = None) -> None:
    console_ = Console() if console is None else console
    console_.print(message)


def print_content_not_available(message: str, *, console: Console | None = None) -> None:
    full_message = colorize_content_not_available(message)
    print_cli(full_message, console=console)


def print_ok(message: str, *, prefix: bool = True, console: Console | None = None) -> None:
    prefix_ = "[b]OK:[/] " if prefix else ""
    full_message = colorize_ok(prefix_ + message)
    print_cli(full_message, console=console)


def print_info(message: str, *, prefix: bool = True, console: Console | None = None) -> None:
    prefix_ = "[b]Info:[/] " if prefix else ""
    full_message = prefix_ + message
    print_cli(full_message, console=console)


def print_warning(message: str, *, prefix: bool = True, console: Console | None = None) -> None:
    prefix_ = "[b]Warning:[/] " if prefix else ""
    full_message = colorize_warning(prefix_ + message)
    print_cli(full_message, console=console)


def print_error(message: str, *, prefix: bool = True, console: Console | None = None) -> None:
    prefix_ = "[b]Error:[/] " if prefix else ""
    full_message = colorize_error(prefix_ + message)
    print_cli(full_message, console=console)


def print_json(message: str, *, console: Console | None = None) -> None:
    console_ = Console() if console is None else console
    console_.print_json(message)
