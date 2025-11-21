from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, get_args

import test_tools as tt

if TYPE_CHECKING:
    from clive_local_tools.cli.result_wrapper import CLITestResult


class CLITestCommandError(AssertionError):
    def __init__(self, result: CLITestResult) -> None:
        message = f"Command failed\n\n{result.info}"
        tt.logger.error(message)
        super().__init__(message)
        self.result = result


class UnsupportedOptionError(Exception):
    def __init__(self, supported_type: TypeAlias, actual_type: TypeAlias) -> None:
        supported_type_names = [arg.__name__ for arg in get_args(supported_type)]
        super().__init__(f"unsupported type, supported types are {supported_type_names}, actual type was {actual_type}")
