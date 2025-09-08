from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.cli.print_cli import print_error, print_info, print_warning

if TYPE_CHECKING:
    from clive.__private.core.types import NotifyLevel


def notify(message: str, *, level: NotifyLevel = "info") -> None:
    if level == "error":
        print_error(message)
    elif level == "warning":
        print_warning(message)
    else:
        print_info(message)
