from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import Result


@dataclass
class CLITestResult:
    _click_result: Result
    command: list[str]
    stdin: str | None = None

    @property
    def exit_code(self) -> int:
        return self._click_result.exit_code

    @property
    def info(self) -> str:
        f"The exit code of the command `{self.command}` was: {self.exit_code}.\nOutput:\n{self.output}"

    @property
    def output(self) -> str:
        return self._click_result.output

    @property
    def stdout(self) -> str:
        return self._click_result.stdout
