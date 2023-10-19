from __future__ import annotations

from click import ClickException


class CLIPrettyError(ClickException):
    """
    A pretty error to be shown to the user.

    Example:
    -------
    >>> raise CLIPrettyError("some message")
    ╭─ Error ───────────────────────────────────────────────────╮
    │ some message                                              │
    ╰───────────────────────────────────────────────────────────╯
    """

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code
