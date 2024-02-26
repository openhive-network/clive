from __future__ import annotations


class CliveCommandError(Exception):
    def __init__(self, stdout: str, exit_code: int, command: list[str]) -> None:
        super().__init__(stdout)
        self.exit_code = exit_code
        self.command = command
