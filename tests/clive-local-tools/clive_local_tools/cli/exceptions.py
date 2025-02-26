from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, TypeAlias, get_args

if TYPE_CHECKING:
    from types import TracebackType

    from click.testing import Result


class CLITestCommandError(AssertionError):
    def __init__(self, command: list[str], exit_code: int, stdout: str, result: Result) -> None:
        message = f"Command {command} failed because of {exit_code=}.\n\nOutput:\n{stdout}"
        if result.exception:
            assert result.exc_info is not None, "exc_info should be set when exception is set."
            tb: TracebackType = result.exc_info[2]
            tb_formatted = "".join(traceback.format_tb(tb))
            message += f"\nException:\n{result.exception!r}\n\nTraceback:\n{tb_formatted}"
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.result = result


class UnsupportedOptionError(Exception):
    def __init__(self, supported_type: TypeAlias, actual_type: TypeAlias) -> None:
        supported_type_names = [arg.__name__ for arg in get_args(supported_type)]
        super().__init__(f"unsupported type, supported types are {supported_type_names}, actual type was {actual_type}")
