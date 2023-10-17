from __future__ import annotations

from click import ClickException


class CLIError(ClickException):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code
