from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
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
            self._error = exc_val
            try:
                self._handle_error(exc_val)
            except Exception:  # noqa: BLE001
                return False
            else:
                return True
        return False

    @abstractmethod
    def _handle_error(self, error: Exception) -> ResultNotAvailable:
        """Handle all the errors. Reraise if error should not be handled."""

    @property
    def error(self) -> Exception | None:
        return self._error

    @property
    def error_occurred(self) -> bool:
        return self.error is not None

    def execute(self, func: Callable[[], ExecuteResultT]) -> ExecuteResultT | ResultNotAvailable:
        try:
            return func()
        except Exception as error:  # noqa: BLE001
            self._error = error
            return self._handle_error(error)
