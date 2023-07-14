from __future__ import annotations

from typing import Final

from clive.__private.core.clive_import import get_clive
from clive.__private.core.error_handlers.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)
from clive.__private.logger import logger
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import CommunicationError


class CommunicationFailureNotificator(ErrorHandlerContextManager):
    """A context manager that notifies about errors of `CommunicatorError` type."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "does not have sufficient funds": "You don't have enough funds to perform this operation.",
    }

    def _handle_error(self, error: BaseException) -> ResultNotAvailable:
        if isinstance(error, CommunicationError):
            self.__notify(error)
            return ResultNotAvailable(error)
        raise error

    def __notify(self, exception: CommunicationError) -> None:
        message = self.__determine_message(exception)

        if get_clive().is_launched:
            self.__notify_tui(message)
            return

        logger.warning(f"Command failed and no one was notified. {message=}")

    @classmethod
    def __determine_message(cls, exception: CommunicationError) -> str:
        exception_raw = str(exception)

        for searched, printed in cls.SEARCHED_AND_PRINTED_MESSAGES.items():
            if searched in exception_raw:
                return printed
        return exception_raw

    @staticmethod
    def __notify_tui(message: str) -> None:
        Notification(message, category="error").show()
