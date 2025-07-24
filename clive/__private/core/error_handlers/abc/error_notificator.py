from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from clive.__private.core.clive_import import get_clive
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)

if TYPE_CHECKING:
    from types import TracebackType


class ErrorNotificatorError(Exception):
    """Base class for exceptions raised by ErrorNotificator."""


class CannotNotifyError(ErrorNotificatorError):
    def __init__(self, error: Exception, reason: str) -> None:
        self.error = error
        self.reason = reason
        self.message = f"Error occurred, but no one was notified: {reason}"
        super().__init__(self.message)


class ErrorNotificator[ExceptionT: Exception](ErrorHandlerContextManager[ExceptionT], ABC):
    """A context manager that notifies about errors."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Return false if exception should be re-raised."""
        if exc_val is not None and isinstance(exc_val, Exception):
            try:
                await self.try_to_handle_error(exc_val)
            except CannotNotifyError:
                # returning false would result in incorrect error being thrown
                raise
            except Exception:  # noqa: BLE001
                return False
            else:
                return True
        return False

    @abstractmethod
    def _determine_message(self, exception: ExceptionT) -> str:
        """Return message to be displayed in notification."""

    def _handle_error(self, error: ExceptionT) -> ResultNotAvailable:
        self._notify(error)
        return ResultNotAvailable(error)

    def _notify(self, exception: ExceptionT) -> None:
        message = self._determine_message(exception)

        if get_clive().is_launched():
            self._notify_tui(message)
            return

        raise CannotNotifyError(exception, message)

    def _notify_tui(self, message: str) -> None:
        """
        Notify about the error in TUI.

        Args:
            message: The message to display in the notification.
        """
        get_clive().app_instance().notify(message, severity="error")
