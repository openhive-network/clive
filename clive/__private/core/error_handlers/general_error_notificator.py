from __future__ import annotations

from typing import Final, TypeGuard

from beekeepy.exceptions import InvalidPasswordError, NoWalletWithSuchNameError

from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator


class GeneralErrorNotificator(ErrorNotificator[Exception]):
    """A context manager that notifies about any catchable errors that are not handled by other notificators."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[type[Exception], str]] = {
        InvalidPasswordError: "The password you entered is incorrect. Please try again.",
        NoWalletWithSuchNameError: "Wallet with this name was not found on the beekeeper. Please try again.",
    }

    def __init__(self) -> None:
        super().__init__()
        self._message_to_print = "Something went wrong. Please try again."

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[Exception]:
        for searched, printed in self.SEARCHED_AND_PRINTED_MESSAGES.items():
            if type(error) is searched:
                self._message_to_print = printed
                return True
        return False

    def _determine_message(self, _: Exception) -> str:
        return self._message_to_print
