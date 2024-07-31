from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, get_args

if TYPE_CHECKING:
    from click.testing import Result


class CLITestCommandError(AssertionError):
    def __init__(self, command: list[str], exit_code: int, stdout: str, result: Result) -> None:
        message = f"command {command} failed because of {exit_code=}. Output:\n{stdout}"
        if result.exception:
            message += f"\nException occurred:\n{result.exception!r}"
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.result = result


class UnsupportedOptionError(Exception):
    def __init__(self, supported_type: TypeAlias, actual_type: TypeAlias) -> None:
        supported_type_names = [arg.__name__ for arg in get_args(supported_type)]
        super().__init__(f"unsupported type, supported types are {supported_type_names}, actual type was {actual_type}")
