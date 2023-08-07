from __future__ import annotations

from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)
from clive.__private.logger import logger


class AsyncClosedErrorHandler(ErrorHandlerContextManager):
    """A context manager that notifies about errors."""

    def _try_to_handle_error(self, error: Exception) -> ResultNotAvailable:
        if isinstance(error, AssertionError) and "Session is closed" in str(error):
            logger.warning("Suppressed `Session is closed` exception, application is closing?")
            return ResultNotAvailable(error)
        raise error
