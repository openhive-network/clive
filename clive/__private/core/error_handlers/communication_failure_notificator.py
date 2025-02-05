from __future__ import annotations

from typing import Final, TypeGuard

from helpy.exceptions import CommunicationError, TimeoutExceededError

from clive.__private.core.clive_import import get_clive
from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator


class CommunicationFailureNotificator(ErrorNotificator[CommunicationError]):
    """A context manager that notifies about errors of `CommunicatorError` type."""

    YOU_DONT_HAVE_ENOUGH_FUNDS_MESSAGE: Final[str] = "You don't have enough funds to perform this operation."

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "does not have sufficient funds": YOU_DONT_HAVE_ENOUGH_FUNDS_MESSAGE,
    }

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[CommunicationError]:
        return isinstance(error, CommunicationError)

    @classmethod
    def _determine_message(cls, exception: CommunicationError) -> str:
        if isinstance(exception, TimeoutExceededError):
            return cls._get_communication_timeout_message(exception)

        error_messages = exception.get_response_error_messages()
        url = exception.url

        if not error_messages:
            return cls._get_communication_not_available_message(url)

        replaced: list[str] = []
        for error_message in error_messages:
            for searched_message, replaced_message in cls.SEARCHED_AND_PRINTED_MESSAGES.items():
                if searched_message in error_message:
                    replaced.append(replaced_message)
                    break
            else:
                replaced.append(error_message)

        error_details = replaced[0] if len(replaced) == 1 else str(replaced)
        return cls._get_communication_detailed_error_message(url, error_details)

    def _notify_tui(self, message: str) -> None:
        """
        Notify about the error in TUI if it's necessary.

        Notifies always only if the error response is available because if there is no response,
        it indicates general connection issue and no need to notify user about it multiple times
        because that causes a lot of notifications.
        """

        def is_error_response_available() -> bool:
            return self.error_ensure.response is not None

        if is_error_response_available():
            super()._notify_tui(message)
            return

        clive_app = get_clive().app_instance()
        if clive_app.is_notification_present(message):
            return

        super()._notify_tui(message)

    @staticmethod
    def _get_communication_not_available_message(url: str) -> str:
        return f"Could not communicate with (seems to be unavailable): {url}"

    @staticmethod
    def _get_communication_detailed_error_message(url: str, error_details: str) -> str:
        return f"Communication error with {url}:\n{error_details}"

    @staticmethod
    def _get_communication_timeout_message(exception: TimeoutExceededError) -> str:
        return (
            f"Timeout occurred during communication with {exception.url}."
            f" Took over {exception.timeout_secs:.2f} seconds."
        )
