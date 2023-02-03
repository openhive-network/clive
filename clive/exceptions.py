from abc import ABC, abstractmethod
from typing import Dict


class CliveException(Exception):
    """Base class for all clive exceptions."""


class ViewException(CliveException):
    """Base class for all view exceptions."""


class ViewDoesNotExist(ViewException):
    """Raised when a view does not exist."""


class FloatException(CliveException, ABC):
    def info(self) -> str:
        return self._get_info()

    @abstractmethod
    def _get_info(self) -> str:
        """Returns formatted information about exception"""


class FormNotFinishedException(FloatException):
    """Raised when user choose to finish, but form is not finished"""

    def __init__(self, **kwargs: bool) -> None:
        self.exception_message = self.__format_exception(kwargs)
        super().__init__()

    def _get_info(self) -> str:
        return self.exception_message

    def __format_exception(self, report: Dict[str, bool]) -> str:
        return "Form completion report\n\n" + "\n".join(
            [f'    - {key} = {("OK" if value else "FAIL")}' for key, value in report.items()]
        )


class FileFloatException(FloatException):
    def __init__(self, filename: str) -> None:
        self._filename = filename
        super().__init__()


class FileDoesNotExists(FileFloatException):
    def _get_info(self) -> str:
        return f"File `{self._filename} not found!"


class FileIsEmpty(FileFloatException):
    def _get_info(self) -> str:
        return f"File `{self._filename}` was found, but is empty!"


class NoMatch(FloatException):
    def __init__(self, string: str, regex: str) -> None:
        self.__string = string
        self.__regex = regex

    def _get_info(self) -> str:
        return f"""Given input:
`{self.__string}`

Does not match following regex:

`{self.__regex}`
"""


class NotInValidRange(FloatException):
    def __init__(self, value: float, min_range: float, max_range: float) -> None:
        self.__value = value
        self.__min_range = min_range
        self.__max_range = max_range

    def _get_info(self) -> str:
        return f"""Given input: `{self.__value}`
does not fit required range:
<{self.__min_range} ; {self.__max_range}>"""


class InvalidHost(FloatException):
    def _get_info(self) -> str:
        return "Given hostname/address is not valid!"
