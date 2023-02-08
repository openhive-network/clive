from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class CliveError(Exception):
    """Base class for all clive exceptions."""


class ViewError(CliveError):
    """Base class for all view exceptions."""


class ViewDoesNotExistError(ViewError):
    """Raised when a view does not exist."""


class FloatError(CliveError, ABC):
    def info(self) -> str:
        return self._get_info()

    @abstractmethod
    def _get_info(self) -> str:
        """Returns formated informations about exception"""


class FormNotFinishedError(FloatError):
    """Raised when user choose to finish, but form is not finished"""

    def __init__(self, **kwargs: bool) -> None:
        self.exception_message = self.__format_exception(kwargs)
        super().__init__(self.exception_message)

    def _get_info(self) -> str:
        return self.exception_message

    def __format_exception(self, report: Dict[str, bool]) -> str:
        return "Form completion report\n\n" + "\n".join(
            [f'    - {key} = {("OK" if value else "FAIL")}' for key, value in report.items()]
        )


class KeyBindingError(CliveError):
    """Base class for all key binding exceptions."""
