from __future__ import annotations

from typing import Final, TypeGuard

from clive.__private.core.clive_import import get_clive
from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator
from clive.dev import is_in_dev_mode
from clive.exceptions import CommunicationError, CommunicationTimeoutError


class CommunicationFailureNotificator(ErrorNotificator[CommunicationError]):
    """A context manager that notifies about errors of `CommunicatorError` type."""

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[str, str]] = {
        "does not have sufficient funds": "You don't have enough funds to perform this operation.",
    }

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[CommunicationError]:
        return isinstance(error, CommunicationError)

    @classmethod
    def _determine_message(cls, exception: CommunicationError) -> str:
        if isinstance(exception, CommunicationTimeoutError):
            return cls._get_communication_timeout_message(exception)

        error_messages = exception.get_response_error_messages()
        url = exception.url

        if not error_messages:
            return cls._get_communication_detailed_error_message(url, "No error details available.")

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

        Presents explicit error message always in dev mode for debugging purposes
        or if response is available because if there is no response, it indicates general connection issue
        and no need to notify user about it multiple times and show request details because that causes a lot of long
        and unreadable notifications.
        """
        error = self.error_ensure

        def should_notify_with_explicit_error() -> bool:
            return is_in_dev_mode() or error.is_response_available

        if should_notify_with_explicit_error():
            super()._notify_tui(message)
            return

        clive_app = get_clive().app_instance()
        notification_content = self._get_communication_not_available_message(error.url)
        if clive_app.is_notification_present(notification_content):
            return

        super()._notify_tui(notification_content)

    @staticmethod
    def _get_communication_not_available_message(url: str) -> str:
        return f"Could not communicate with (seems to be unavailable): {url}"

    @staticmethod
    def _get_communication_detailed_error_message(url: str, error_details: str) -> str:
        return f"Communication error with {url}:\n{error_details}"

    @staticmethod
    def _get_communication_timeout_message(exception: CommunicationTimeoutError) -> str:
        return str(exception)
