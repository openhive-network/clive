from __future__ import annotations

from abc import ABC, abstractmethod

from clive.__private.core.clive_import import get_clive
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)
from clive.__private.logger import logger


class ErrorNotificator(ErrorHandlerContextManager, ABC):
    """A context manager that notifies about errors."""

    @abstractmethod
    def _determine_message(self, exception: Exception) -> str:
        """Return message to be displayed in notification."""

    def _handle_error(self, error: Exception) -> ResultNotAvailable:
        self.__notify(error)
        return ResultNotAvailable(error)

    def __notify(self, exception: Exception) -> None:
        message = self._determine_message(exception)

        if get_clive().is_launched:
            self.__notify_tui(message)
            return

        logger.warning(f"Command failed and no one was notified. {message=}")

    @staticmethod
    def __notify_tui(message: str) -> None:
        get_clive().app_instance().notify(message, severity="error")
