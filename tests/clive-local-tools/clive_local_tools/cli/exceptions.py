from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import Result


class CliveCommandError(AssertionError):
    def __init__(self, command: list[str], exit_code: int, stdout: str, result: Result) -> None:
        super().__init__(f"command {command} failed")
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.result = result
