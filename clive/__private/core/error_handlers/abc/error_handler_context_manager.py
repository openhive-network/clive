from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypeGuard, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from types import TracebackType
    from typing import Self

ExecuteResultT = TypeVar("ExecuteResultT")
ExceptionT = TypeVar("ExceptionT", bound=Exception)
AnyErrorHandlerContextManager: TypeAlias = "ErrorHandlerContextManager[Any]"


@dataclass
class ResultNotAvailable:
    exception: Exception


class ErrorHandlerContextManager(Generic[ExceptionT], ABC):
    def __init__(self) -> None:
        self._error: Exception | None = None

    async def __aenter__(self) -> Self:
        return self

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
            except Exception:  # noqa: BLE001
                return False
            else:
                return True
        return False

    @abstractmethod
    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[ExceptionT]:
        """Return `True` if the exception should be caught."""

    @abstractmethod
    def _handle_error(self, error: ExceptionT) -> ResultNotAvailable:
        """Handle all the errors. Reraise if error should not be handled. Return `ResultNotAvailable` otherwise."""

    async def try_to_handle_error(self, error: Exception) -> ResultNotAvailable:
        self._error = error
        if self._is_exception_to_catch(error):
            return self._handle_error(error)
        raise error

    @property
    def error(self) -> Exception | None:
        return self._error

    @property
    def error_ensure(self) -> ExceptionT:
        error = self.error
        assert error is not None, "Error is not available"
        assert self._is_exception_to_catch(error), f"Error {error} is not the expected one"
        return error

    @property
    def error_occurred(self) -> bool:
        return self.error is not None

    async def execute(self, async_func: Awaitable[ExecuteResultT]) -> ExecuteResultT | ResultNotAvailable:
        try:
            return await async_func
        except Exception as error:  # noqa: BLE001
            return await self.try_to_handle_error(error)
