from __future__ import annotations

from typing import TypeGuard

from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)
from clive.__private.logger import logger


class AsyncClosedErrorHandler(ErrorHandlerContextManager[AssertionError]):
    """A context manager that notifies about errors."""

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[AssertionError]:
        return isinstance(error, AssertionError) and "Session is closed" in str(error)

    def _handle_error(self, error: AssertionError) -> ResultNotAvailable:
        logger.warning("Suppressed `Session is closed` exception, application is closing?")
        return ResultNotAvailable(error)
