from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from types import TracebackType

    from typing_extensions import Self

ExecuteResultT = TypeVar("ExecuteResultT")


@dataclass
class ResultNotAvailable:
    exception: Exception


class ErrorHandlerContextManager(ABC):
    def __init__(self) -> None:
        self._error: Exception | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Return false if exception should be re-raised."""
        if exc_val is not None and isinstance(exc_val, Exception):
            try:
                asyncio_run(self.try_to_handle_error(exc_val))
            except Exception:  # noqa: BLE001
                return False
            else:
                return True
        return False

    @abstractmethod
    def _try_to_handle_error(self, error: Exception) -> ResultNotAvailable:
        """Handle all the errors. Reraise if error should not be handled. Return `ResultNotAvailable` otherwise."""

    async def try_to_handle_error(self, error: Exception) -> ResultNotAvailable:
        self._error = error
        return self._try_to_handle_error(error)

    @property
    def error(self) -> Exception | None:
        return self._error

    @property
    def error_occurred(self) -> bool:
        return self.error is not None

    async def execute(self, async_func: Awaitable[ExecuteResultT]) -> ExecuteResultT | ResultNotAvailable:
        try:
            return await async_func
        except Exception as error:  # noqa: BLE001
            return await self.try_to_handle_error(error)
