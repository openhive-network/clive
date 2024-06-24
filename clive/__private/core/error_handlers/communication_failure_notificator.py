from __future__ import annotations

from typing import Final, TypeGuard

from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator
from clive.exceptions import CommunicationError


class CommunicationFailureNotificator(ErrorNotificator[CommunicationError]):
    """A context manager that notifies about errors of `CommunicatorError` type."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "does not have sufficient funds": "You don't have enough funds to perform this operation.",
    }

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[CommunicationError]:
        return isinstance(error, CommunicationError)

    @classmethod
    def _determine_message(cls, exception: CommunicationError) -> str:
        error_messages = exception.get_response_error_messages()

        if not error_messages:
            return str(exception)

        replaced = [
            printed for searched, printed in cls.SEARCHED_AND_PRINTED_MESSAGES.items() if searched in error_messages
        ]
        return str(replaced) if replaced else str(error_messages)
