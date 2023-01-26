from typing import Dict


class CliveException(Exception):
    """Base class for all clive exceptions."""


class ViewException(CliveException):
    """Base class for all view exceptions."""


class ViewDoesNotExist(ViewException):
    """Raised when a view does not exist."""


class FormNotFinishedException(ViewException):
    """Raised when user choose to finish, but form is not finished"""

    def __init__(self, **kwargs: bool) -> None:
        self.exception_message = self.__format_exception(kwargs)
        super().__init__(self.exception_message)

    def __format_exception(self, report: Dict[str, bool]) -> str:
        return "Form completion report\n" + "\n".join(
            [f'{key} = {("OK" if value else "FAIL")}' for key, value in report.items()]
        )
