from __future__ import annotations

from typing import Final

from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator


class GeneralErrorNotificator(ErrorNotificator):
    """A context manager that notifies about any catchable errors that are not handled by other notificators."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "Invalid password for wallet": "The password you entered is incorrect. Please try again.",
    }

    def __init__(self) -> None:
        super().__init__()
        self.__message_to_print = "Something went wrong. Please try again."

    def _is_exception_to_catch(self, error: BaseException) -> bool:
        for searched, printed in self.SEARCHED_AND_PRINTED_MESSAGES.items():
            if searched in str(error):
                self.__message_to_print = printed
                return True
        return False

    def _determine_message(self, _: BaseException) -> str:
        return self.__message_to_print
