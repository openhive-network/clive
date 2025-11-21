from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.constants.env import ENTRYPOINT

if TYPE_CHECKING:
    from types import TracebackType

    from click.testing import Result


@dataclass
class CLITestResult:
    _click_result: Result
    command: list[str]
    stdin: str | None = None

    @property
    def command_pretty(self) -> str:
        return f"{ENTRYPOINT} " + " ".join(self.command)

    @property
    def exception(self) -> BaseException | None:
        return self._click_result.exception

    @property
    def exit_code(self) -> int:
        return self._click_result.exit_code

    @property
    def info(self) -> str:
        message = f"The exit code of the command `{self.command_pretty}` was: {self.exit_code}.\n"
        message += f"\nOutput:\n{self.output}"
        if self.exception:
            message += f"\nException:\n{self.exception!r}"
            message += f"\n{self.traceback_pretty}"
        return message

    @property
    def output(self) -> str:
        return self._click_result.output

    @property
    def stdout(self) -> str:
        return self._click_result.stdout

    @property
    def traceback_pretty(self) -> str | None:
        if self._click_result.exception:
            assert self._click_result.exc_info is not None, "exc_info should be set when exception is set."
            tb: TracebackType = self._click_result.exc_info[2]
            tb_formatted = "".join(traceback.format_tb(tb))
            return f"Traceback:\n{tb_formatted}"
        return None
